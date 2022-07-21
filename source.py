from gi.repository import RB, Gio, GLib, Gdk, Gtk

from album_arts import AlbumArtManager


class YandexMusicSource(RB.BrowserSource):
    def __init__(self):
        RB.BrowserSource.__init__(self)
        self.app = Gio.Application.get_default()

    def setup(self, shell, client, station):
        self.initialised = False
        self.shell = shell
        self.db = shell.props.db
        self.player = shell.props.shell_player
        self.entry_type = self.props.entry_type
        self.client = client
        self.album_arts = AlbumArtManager()
        self.station = station[station.find('_')+1:]
        self.station_prefix = station[:station.find('_')+1]
        self.is_feed = (station.find('feed') == 0)
        self.last_track = None
        self.last_state = None
        if self.is_feed:
            self.player.connect('playing_uri_changed', self.update_feed)

    def load_tracks(self):
        return self.client.rotor_station_tracks(station=self.station, queue=self.last_track).sequence

    def do_selected(self):
        if not self.initialised or self.is_feed:
            self.initialised = True
            Gdk.threads_add_idle(GLib.PRIORITY_DEFAULT_IDLE, self.add_entries)
        if self.is_feed:
            self.last_state = self.player.get_playback_state()
            self.player.set_playback_state(shuffle=False, repeat=False)
        self.add_context_menu()

    def do_deselected(self):
        if self.is_feed:
            self.player.set_playback_state(shuffle=self.last_state.shuffle, repeat=self.last_state.repeat)
        self.remove_context_menu()

    def add_entries(self):
        if self.station_prefix == 'likes_':
            tracks = self.client.users_likes_tracks().fetch_tracks()
        elif self.station_prefix.find('mepl') == 0:
            tracks = self.client.users_playlists(kind=self.station).fetch_tracks()
        elif self.station_prefix.find('likepl') == 0:
            user_id = self.station[:self.station.find(':')]
            album_id = self.station[self.station.find(':')+1:]
            tracks = self.client.users_playlists(kind=album_id, user_id=user_id).fetch_tracks()
        elif self.station_prefix.find('feed') == 0:
            tracks = self.client.rotor_station_tracks(station=self.station, queue=self.last_track).sequence
        else:
            return False
        self.iterator = 0
        self.listcount = len(tracks)
        Gdk.threads_add_idle(GLib.PRIORITY_DEFAULT_IDLE, self.add_entry, tracks)
        return False

    def add_entry(self, tracks):
        try:
            track = tracks[self.iterator].track
        except AttributeError:
            track = tracks[self.iterator]
        if track.available:
            track_location = self.station_prefix+str(track.id)
            if len(track.albums) > 0:
                track_location = track_location+':'+str(track.albums[0].id)
            entry = self.db.entry_lookup_by_location(track_location)
            if not entry:
                entry = RB.RhythmDBEntry.new(self.db, self.entry_type, track_location)
                if entry:
                    self.db.entry_set(entry, RB.RhythmDBPropType.TITLE, track.title)
                    self.db.entry_set(entry, RB.RhythmDBPropType.DURATION, track.duration_ms/1000)
                    artists = ', '.join(artist.name for artist in track.artists)
                    self.db.entry_set(entry, RB.RhythmDBPropType.ARTIST, artists)
                    if len(track.albums) > 0:
                        self.db.entry_set(entry, RB.RhythmDBPropType.ALBUM, track.albums[0].title)
                        self.db.entry_set(entry, RB.RhythmDBPropType.GENRE, str(track.albums[0].genre))
                    self.db.commit()
                    self.album_arts.ensure_art_exists(track)
        self.iterator += 1
        if self.iterator >= self.listcount:
            self.last_track = str(track.id)+':'+str(track.albums[0].id)
            return False
        else:
            return True

    def update_feed(self, player, uri):
        if not uri or uri[:uri.find('_')+1] != self.station_prefix: return
        Gdk.threads_add_idle(GLib.PRIORITY_DEFAULT_IDLE, self.add_entries)

    def add_context_menu(self):
        if self.station_prefix == 'likes_':
            action = Gio.SimpleAction(name='ym-'+self.station_prefix+'unlikes')
            action.connect('activate', self.unlike_tracks)
            self.app.add_action(action)
            item = Gio.MenuItem()
            item.set_label(_('Не нравится'))
            item.set_detailed_action('app.ym-'+self.station_prefix+'unlikes')
            self.app.add_plugin_menu_item('browser-popup', 'ym-'+self.station_prefix+'unlikes', item)
        else:
            action = Gio.SimpleAction(name='ym-'+self.station_prefix+'likes')
            action.connect('activate', self.like_tracks)
            self.app.add_action(action)
            item = Gio.MenuItem()
            item.set_label(_('Мне нравится'))
            item.set_detailed_action('app.ym-'+self.station_prefix+'likes')
            self.app.add_plugin_menu_item('browser-popup', 'ym-'+self.station_prefix+'likes', item)
        action = Gio.SimpleAction(name='ym-'+self.station_prefix+'dislikes')
        action.connect('activate', self.dislike_tracks)
        self.app.add_action(action)
        item = Gio.MenuItem()
        item.set_label(_('Не рекомендовать'))
        item.set_detailed_action('app.ym-'+self.station_prefix+'dislikes')
        self.app.add_plugin_menu_item('browser-popup', 'ym-'+self.station_prefix+'dislikes', item)

        # Copy track link action
        action_name = 'ym-'+self.station_prefix+'copy_track_link'
        action = Gio.SimpleAction(name=action_name)
        action.connect('activate', self.copy_track_link)
        self.app.add_action(action)
        item = Gio.MenuItem()
        item.set_label(_('Copy link'))
        item.set_detailed_action('app.'+action_name)
        self.app.add_plugin_menu_item('browser-popup', action_name, item)

    def remove_context_menu(self):
        self.app.remove_plugin_menu_item('browser-popup', 'ym-'+self.station_prefix+'likes')
        self.app.remove_plugin_menu_item('browser-popup', 'ym-'+self.station_prefix+'unlikes')
        self.app.remove_plugin_menu_item('browser-popup', 'ym-'+self.station_prefix+'dislikes')
        self.app.remove_plugin_menu_item('browser-popup', 'ym-'+self.station_prefix+'copy_track_link')

    def like_tracks(self, *args):
        page = self.shell.props.selected_page
        selected = page.get_entry_view().get_selected_entries()
        if not selected: return False
        tracks = []
        for entry in selected:
            location = entry.get_string(RB.RhythmDBPropType.LOCATION)
            location = location[location.find('_')+1:]
            tracks.append(location)
        return self.client.users_likes_tracks_add(track_ids=tracks)

    def unlike_tracks(self, *args):
        page = self.shell.props.selected_page
        selected = page.get_entry_view().get_selected_entries()
        if not selected: return False
        tracks = []
        for entry in selected:
            location = entry.get_string(RB.RhythmDBPropType.LOCATION)
            location = location[location.find('_')+1:]
            tracks.append(location)
        if self.client.users_likes_tracks_remove(track_ids=tracks):
            for entry in selected:
                self.db.entry_delete(entry)
            return self.db.commit()
        return False

    def dislike_tracks(self, *args):
        page = self.shell.props.selected_page
        selected = page.get_entry_view().get_selected_entries()
        if not selected: return False
        tracks = []
        for entry in selected:
            location = entry.get_string(RB.RhythmDBPropType.LOCATION)
            location = location[location.find('_')+1:]
            tracks.append(location)
        if self.client.users_dislikes_tracks_add(track_ids=tracks):
            for entry in selected:
                self.db.entry_delete(entry)
            self.db.commit()
            return self.shell.props.shell_player.do_next()
        return False

    def copy_track_link(self, *args):
        """Copy a link to the track page on Yandex.Music."""
        page = self.shell.props.selected_page
        selected = page.get_entry_view().get_selected_entries()
        if len(selected) != 1:
            return False
        location = selected[0].get_string(RB.RhythmDBPropType.LOCATION)
        track_id, album_id = location[location.find('_')+1:].split(':')
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        clipboard.set_text(f'https://music.yandex.ru/album/{album_id}/track/{track_id}', -1)

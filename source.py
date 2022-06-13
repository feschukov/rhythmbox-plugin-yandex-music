from gi.repository import RB, Gio, GLib, Gdk

class YandexMusicSource(RB.BrowserSource):
    def __init__(self):
        RB.BrowserSource.__init__(self)
        self.app = Gio.Application.get_default()

    def setup(self, shell, client, station):
        self.initialised = False
        self.shell = shell
        self.db = shell.props.db
        self.entry_type = self.props.entry_type
        self.client = client
        self.station = station[station.find('_')+1:]
        self.station_prefix = station[:station.find('_')+1]
        self.is_feed = (station.find('feed') == 0)
        self.last_track = None

    def load_tracks(self):
        return self.client.rotor_station_tracks(station=self.station, queue=self.last_track).sequence

    def do_selected(self):
        if not self.initialised or self.is_feed:
            self.initialised = True
            Gdk.threads_add_idle(GLib.PRIORITY_DEFAULT_IDLE, self.add_entries)
        self.add_context_menu()

    def do_deselected(self):
        self.remove_context_menu()

    def add_entries(self):
        if self.station_prefix == 'likes_':
            tracks = self.client.users_likes_tracks().fetch_tracks()
        elif self.station_prefix.find('mepl') == 0:
            tracks = self.client.users_playlists(kind=self.station).fetch_tracks()
        elif self.station_prefix.find('likepl') == 0:
            user_id  = self.station[:self.station.find(':')]
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
            if entry is None:
                entry = RB.RhythmDBEntry.new(self.db, self.entry_type, track_location)
                if entry is not None:
                    self.db.entry_set(entry, RB.RhythmDBPropType.TITLE, track.title)
                    self.db.entry_set(entry, RB.RhythmDBPropType.DURATION, track.duration_ms/1000)
                    artists = ''
                    for artist in track.artists:
                        if len(artists) > 1:
                            artists += ', '+artist.name
                        else:
                            artists = artist.name
                    self.db.entry_set(entry, RB.RhythmDBPropType.ARTIST, artists)
                    if len(track.albums) > 0:
                        self.db.entry_set(entry, RB.RhythmDBPropType.ALBUM, track.albums[0].title)
                    self.db.commit()
        self.iterator += 1
        if self.iterator >= self.listcount:
            self.last_track = str(track.id)+':'+str(track.albums[0].id)
            return False
        else:
            return True

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

    def remove_context_menu(self):
        self.app.remove_plugin_menu_item('browser-popup', 'ym-'+self.station_prefix+'likes')
        self.app.remove_plugin_menu_item('browser-popup', 'ym-'+self.station_prefix+'unlikes')
        self.app.remove_plugin_menu_item('browser-popup', 'ym-'+self.station_prefix+'dislikes')

    def like_tracks(self, *args):
        page = self.shell.props.selected_page
        selected = page.get_entry_view().get_selected_entries()
        if selected:
            tracks = []
            for entry in selected:
                location = entry.get_string(RB.RhythmDBPropType.LOCATION)
                location = location[location.find('_')+1:]
                tracks.append(location)
            return self.client.users_likes_tracks_add(track_ids=tracks)
        return False

    def unlike_tracks(self, *args):
        page = self.shell.props.selected_page
        selected = page.get_entry_view().get_selected_entries()
        if selected:
            tracks = []
            for entry in selected:
                location = entry.get_string(RB.RhythmDBPropType.LOCATION)
                location = location[location.find('_')+1:]
                tracks.append(location)
            return self.client.users_likes_tracks_remove(track_ids=tracks)
        return False

    def dislike_tracks(self, *args):
        page = self.shell.props.selected_page
        selected = page.get_entry_view().get_selected_entries()
        if selected:
            tracks = []
            for entry in selected:
                location = entry.get_string(RB.RhythmDBPropType.LOCATION)
                location = location[location.find('_')+1:]
                tracks.append(location)
            if self.client.users_dislikes_tracks_add(track_ids=tracks):
                return self.shell.props.shell_player.do_next()
        return False

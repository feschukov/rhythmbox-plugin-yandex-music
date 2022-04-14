from gi.repository import RB, GLib, Gdk

class YMLikesEntry(RB.RhythmDBEntryType):
    def __init__(self, client):
        RB.RhythmDBEntryType.__init__(self, name='ym-likes-type', save_to_disk=False)
        self.client = client

    def do_get_playback_uri(self, entry):
        track_id = entry.get_string(RB.RhythmDBPropType.LOCATION)[6:]
        downinfo = self.client.tracks_download_info(track_id=track_id, get_direct_links=True)
        return downinfo[1].direct_link

    def do_destroy_entry(self, entry):
        track_id = entry.get_string(RB.RhythmDBPropType.LOCATION)
        return self.client.users_likes_tracks_remove(track_ids=track_id)

class YMLikesSource(RB.BrowserSource):
    def __init__(self):
        RB.BrowserSource.__init__(self)

    def setup(self, db, client):
        self.initialised = False
        self.db = db
        self.entry_type = self.props.entry_type
        self.client = client

    def do_selected(self):
        if not self.initialised:
            self.initialised = True
            Gdk.threads_add_idle(GLib.PRIORITY_DEFAULT_IDLE, self.users_likes_tracks)

    def users_likes_tracks(self):
        tracks = self.client.users_likes_tracks().fetch_tracks()
        self.iterator = 0
        self.listcount = len(tracks)
        Gdk.threads_add_idle(GLib.PRIORITY_DEFAULT_IDLE, self.add_entry, tracks)
        return False

    def add_entry(self, tracks):
        track = tracks[self.iterator]
        if track.available:
            entry = self.db.entry_lookup_by_location('likes_'+str(track.id)+':'+str(track.albums[0].id))
            if entry is None:
                entry = RB.RhythmDBEntry.new(self.db, self.entry_type, 'likes_'+str(track.id)+':'+str(track.albums[0].id))
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
                    self.db.entry_set(entry, RB.RhythmDBPropType.ALBUM, track.albums[0].title)
                    self.db.commit()
        self.iterator += 1
        if self.iterator >= self.listcount:
            return False
        else:
            return True

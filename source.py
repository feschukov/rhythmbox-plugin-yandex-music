from gi.repository import RB, GLib, Gdk

class YandexMusicSource(RB.BrowserSource):
    def __init__(self):
        RB.BrowserSource.__init__(self)

    def setup(self, db, client, station):
        self.initialised = False
        self.db = db
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

    def add_entries(self):
        if self.station_prefix == 'likes_':
            tracks = self.client.users_likes_tracks().fetch_tracks()
        elif self.station_prefix.find('feed') == 0:
            tracks = self.client.rotor_station_tracks(station=self.station, queue=self.last_track).sequence
        elif self.station_prefix.find('mepl') == 0:
            tracks = self.client.users_playlists(self.station).fetch_tracks()
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
            entry = self.db.entry_lookup_by_location(self.station_prefix+str(track.id)+':'+str(track.albums[0].id))
            if entry is None:
                entry = RB.RhythmDBEntry.new(self.db, self.entry_type, self.station_prefix+str(track.id)+':'+str(track.albums[0].id))
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
            self.last_track = str(track.id)+':'+str(track.albums[0].id)
            return False
        else:
            return True

from gi.repository import RB, GLib, Gdk

class YMFeedEntry(RB.RhythmDBEntryType):
    def __init__(self, db, client, station):
        RB.RhythmDBEntryType.__init__(self, name='ym-feed-entry', save_to_disk=False)
        self.db = db
        self.client = client
        self.station = station[6:]
        self.last_track = None
        self.last_duration = None

    def do_get_playback_uri(self, entry):
        new_track = entry.get_string(RB.RhythmDBPropType.LOCATION)[6:]
        if (self.last_track is not None) and (self.last_track != new_track):
            self.client.rotor_station_feedback_track_finished(station=self.station, track_id=self.last_track, total_played_seconds=self.last_duration)
        uri = None #entry.get_string(RB.RhythmDBPropType.MOUNTPOINT)
        if uri is None:
            downinfo = self.client.tracks_download_info(track_id=new_track, get_direct_links=True)
            uri = downinfo[1].direct_link
            self.db.entry_set(entry, RB.RhythmDBPropType.MOUNTPOINT, uri)
            self.db.commit()
        if self.last_track != new_track:
            self.client.rotor_station_feedback_track_started(station=self.station, track_id=new_track)
        self.last_track = new_track
        self.last_duration = entry.get_ulong(RB.RhythmDBPropType.DURATION)*1000
        return uri

class YMFeedSource(RB.BrowserSource):
    def __init__(self):
        RB.BrowserSource.__init__(self)

    def setup(self, db, client, station):
        self.initialised = False
        self.db = db
        self.entry_type = self.props.entry_type
        self.client = client
        self.station = station
        self.last_track = None

    def load_tracks(self):
        return self.client.rotor_station_tracks(station=self.station[6:], queue=self.last_track).sequence

    def load_track(self, track):
        return track.track;

    def do_selected(self):
        Gdk.threads_add_idle(GLib.PRIORITY_DEFAULT_IDLE, self.add_entries)

    def add_entries(self):
        tracks = self.load_tracks()
        self.iterator = 0
        self.listcount = len(tracks)
        Gdk.threads_add_idle(GLib.PRIORITY_DEFAULT_IDLE, self.add_entry, tracks)
        return False

    def add_entry(self, tracks):
        track = self.load_track(tracks[self.iterator])
        if track.available:
            entry = self.db.entry_lookup_by_location(self.station[:6]+str(track.id)+':'+str(track.albums[0].id))
            if entry is None:
                entry = RB.RhythmDBEntry.new(self.db, self.entry_type, self.station[:6]+str(track.id)+':'+str(track.albums[0].id))
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

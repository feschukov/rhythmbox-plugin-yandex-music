from gi.repository import RB, GLib, Gdk
import requests

class YandexMusicEntry(RB.RhythmDBEntryType):
    def __init__(self, shell, client, station):
        RB.RhythmDBEntryType.__init__(self, name='ym-'+station[:station.find('_')]+'-entry', save_to_disk=False)
        self.shell = shell
        self.db = shell.props.db
        self.client = client
        self.station = station[station.find('_')+1:]
        self.station_prefix = station[:station.find('_')+1]
        self.is_feed = (station.find('feed') == 0)
        self.last_track = None
        self.last_duration = None

    def do_get_playback_uri(self, entry):
        new_track = entry.get_string(RB.RhythmDBPropType.LOCATION)[len(self.station_prefix):]
        if self.is_feed and self.last_track and self.last_track != new_track:
            Gdk.threads_add_idle(GLib.PRIORITY_LOW, self.feedback_track_finished, self.last_track, self.last_duration)
        uri = entry.get_string(RB.RhythmDBPropType.MOUNTPOINT)
        need_request = uri is None
        if not need_request:
            r = requests.head(uri)
            need_request = (r.status_code != 200)
        if need_request:
            downinfo = self.client.tracks_download_info(track_id=new_track, get_direct_links=True)
            uri = downinfo[1].direct_link
            self.db.entry_set(entry, RB.RhythmDBPropType.MOUNTPOINT, uri)
            self.db.commit()
        if self.is_feed and self.last_track != new_track:
            Gdk.threads_add_idle(GLib.PRIORITY_LOW, self.feedback_track_started, new_track)
        self.last_track = new_track
        self.last_duration = entry.get_ulong(RB.RhythmDBPropType.DURATION)*1000
        return uri

    def can_sync_metadata(self, entry):
        return False

    def do_sync_metadata(self, entry, changes):
        return

    def feedback_track_started(self, track):
        self.client.rotor_station_feedback_track_started(station=self.station, track_id=track)
        return False

    def feedback_track_finished(self, track, duration):
        self.client.rotor_station_feedback_track_finished(station=self.station, track_id=track, total_played_seconds=duration)
        return False

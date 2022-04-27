from gi.repository import RB, GLib, Gdk
from rotor_stations_dashboard import YMFeedSource

class YMUserPlaylistSource(YMFeedSource):
    def load_tracks(self):
        return self.client.users_playlists(self.station[6:]).fetch_tracks()

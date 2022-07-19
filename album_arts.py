from gi.repository import RB

NO_ALBUM = 'UnknownAlbum'


class AlbumArtManager(object):
    def __init__(self):
        self.storage = RB.ExtDB(name="album-art")

    @staticmethod
    def _gen_storage_key(album, artist):
        key = RB.ExtDBKey.create_storage("album", album)
        key.add_field("artist", artist)
        return key

    @staticmethod
    def _gen_lookup_key(album, artist):
        key = RB.ExtDBKey.create_lookup("album", album)
        key.add_field("artist", artist)
        return key

    def ensure_art_exists(self, track, size: str = '200x200'):
        artists = ', '.join(artist.name for artist in track.artists)
        album_title = track.albums[0].title if track.albums else NO_ALBUM
        lookup_key = self._gen_lookup_key(album_title, artists)
        lookup_result = self.storage.lookup(lookup_key)[0]
        if not lookup_result:
            uri = f'https://{track.cover_uri.replace("%%", size)}'
            storage_key = self._gen_storage_key(album_title, artists)
            self.storage.store_uri(storage_key, RB.ExtDBSourceType.SEARCH, uri)

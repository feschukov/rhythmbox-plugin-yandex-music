from gi.repository import GObject, RB, Peas, Gio, GLib, Gdk, Gtk
from yandex_music import Client
import requests

class YandexMusic(GObject.Object, Peas.Activatable):
    object = GObject.property(type=GObject.Object)

    def __init__(self):
        super(YandexMusic, self).__init__()

    def do_activate(self):
        print('Yandex.Music plugin activating')
        schema_source = Gio.SettingsSchemaSource.new_from_directory(self.plugin_info.get_data_dir(), Gio.SettingsSchemaSource.get_default(), False)
        schema = schema_source.lookup('org.gnome.rhythmbox.plugins.yandex-music', False)
        self.settings = Gio.Settings.new_full(schema, None, None)
        shell = self.object
        db = shell.props.db
        self.page_group = RB.DisplayPageGroup(shell=shell, id='yandex-music-playlist', name=_('Яндекс.Музыка'), category=RB.DisplayPageGroupCategory.TRANSIENT)
        shell.append_display_page(self.page_group, None)
        self.entry_type = YMLikesEntry()
        db.register_entry_type(self.entry_type)
        iconfile = Gio.File.new_for_path(self.plugin_info.get_data_dir()+'/yandex-music.svg')
        self.source = GObject.new(YMLikesSource, shell=shell, name=_('Мне нравится'), entry_type=self.entry_type, plugin=self, icon=Gio.FileIcon.new(iconfile))
        self.source.setup(db, self.settings)
        shell.register_entry_type_for_source(self.source, self.entry_type)
        shell.append_display_page(self.source, self.page_group)
        Gdk.threads_add_idle(GLib.PRIORITY_DEFAULT_IDLE, self.load_dashboard)

    def do_deactivate(self):
        print('Yandex.Music plugin deactivating')
        self.source.delete_thyself()
        self.source = None
        self.page_group = None
        self.entry_type = None
        self.client = None
        self.settings = None

    def load_dashboard(self):
        shell = self.object
        db = shell.props.db
        if self.login_yandex():
            dashboard = YMClient.rotor_stations_dashboard()
            for result in dashboard.stations:
                entry_type = YMDashboardEntry(result.station.id.type+':'+result.station.id.tag)
                source = GObject.new(YMDashboardSource, shell=shell, name=result.station.name, entry_type=entry_type, plugin=self)
                source.setup(db, self.settings, result.station.id.type+':'+result.station.id.tag)
                shell.register_entry_type_for_source(source, entry_type)
                shell.append_display_page(source, self.page_group)
        return False

    def login_yandex(self):
        global YMClient
        token = self.settings.get_string('token')
        self.iterator = 0
        while len(token) < 1 and self.iterator < 5:
            d = Gtk.Dialog(buttons=(Gtk.STOCK_OK, Gtk.ResponseType.OK))
            label_login = Gtk.Label(_('Логин'))
            label_passwd = Gtk.Label(_('Пароль'))
            input_login = Gtk.Entry(width_chars=25,activates_default=True)
            input_passwd = Gtk.Entry(width_chars=25,activates_default=True)
            d.vbox.pack_start(label_login, expand=True, fill=True, padding=10)
            d.vbox.pack_start(input_login, expand=False, fill=False, padding=10)
            d.vbox.pack_start(label_passwd, expand=True, fill=True, padding=10)
            d.vbox.pack_start(input_passwd, expand=False, fill=False, padding=10)
            d.show_all()
            d.run()
            login = input_login.get_text()
            password = input_passwd.get_text()
            d.destroy()
            if len(login) > 0 and len(password) > 0:
                token = self.generate_token(login, password)
                if len(token) > 0:
                    self.settings.set_string('token', token)
            self.iterator += 1
        if len(token) < 1:
            return False
        else:
            YMClient = Client(token).init()
            return True

    def generate_token(self, login, password):
        print('Hello');
        link_post = "https://oauth.yandex.com/token"
        user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36"
        header = {
            "user-agent": user_agent
        }
        try:
            request_post = f"grant_type=password&client_id=23cabbbdc6cd418abb4b39c32c41195d&client_secret=53bc75238f0c4d08a118e51fe9203300&username={login}&password={password}"
            request_auth = requests.post(link_post, data=request_post, headers=header)
            if request_auth.status_code == 200:
                json_data = request_auth.json()
                token = json_data.get('access_token')
                return token
            else:
                print('Не удалось получить токен')
        except requests.exceptions.ConnectionError:
            print('Не удалось отправить запрос на получение токена')
        return '';

class YMLikesEntry(RB.RhythmDBEntryType):
    def __init__(self):
        RB.RhythmDBEntryType.__init__(self, name='ym-likes-type', save_to_disk=False)

    def do_get_playback_uri(self, entry):
        global YMClient
        track_id = entry.get_string(RB.RhythmDBPropType.LOCATION)
        downinfo = YMClient.tracks_download_info(track_id=track_id, get_direct_links=True)
        return downinfo[1].direct_link

    def do_destroy_entry(self, entry):
        global YMClient
        track_id = entry.get_string(RB.RhythmDBPropType.LOCATION)
        return YMClient.users_likes_tracks_remove(track_ids=track_id)

class YMLikesSource(RB.BrowserSource):
    def __init__(self):
        RB.BrowserSource.__init__(self)

    def setup(self, db, settings):
        self.initialised = False
        self.db = db
        self.entry_type = self.props.entry_type
        self.settings = settings

    def do_selected(self):
        if not self.initialised:
            self.initialised = True
            Gdk.threads_add_idle(GLib.PRIORITY_DEFAULT_IDLE, self.users_likes_tracks)

    def users_likes_tracks(self):
        global YMClient
        tracks = YMClient.users_likes_tracks().fetch_tracks()
        self.iterator = 0
        self.listcount = len(tracks)
        Gdk.threads_add_idle(GLib.PRIORITY_DEFAULT_IDLE, self.add_entry, tracks)
        return False

    def add_entry(self, tracks):
        track = tracks[self.iterator]
        if track.available:
            entry = RB.RhythmDBEntry.new(self.db, self.entry_type, str(track.id)+':'+str(track.albums[0].id))
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

class YMDashboardEntry(RB.RhythmDBEntryType):
    def __init__(self, station):
        RB.RhythmDBEntryType.__init__(self, name='ym-dashboard-entry', save_to_disk=False)
        self.station = station
        self.last_track = None

    def do_get_playback_uri(self, entry):
        global YMClient
#        if self.last_track:
#            YMClient.rotor_station_feedback_track_finished(station=self.station, track_id=self.last_track, total_played_seconds=entry.get_ulong(RB.RhythmDBPropType.DURATION)*1000)
        self.last_track = entry.get_string(RB.RhythmDBPropType.LOCATION)
        downinfo = YMClient.tracks_download_info(track_id=self.last_track, get_direct_links=True)
#        YMClient.rotor_station_feedback_track_started(station=self.station, track_id=self.last_track)
        return downinfo[1].direct_link

class YMDashboardSource(RB.BrowserSource):
    def __init__(self):
        RB.BrowserSource.__init__(self)

    def setup(self, db, settings, station):
        self.initialised = False
        self.db = db
        self.entry_type = self.props.entry_type
        self.settings = settings
        self.station = station
        self.last_track = None

    def do_selected(self):
        Gdk.threads_add_idle(GLib.PRIORITY_DEFAULT_IDLE, self.rotor_station_tracks)

    def rotor_station_tracks(self):
        global YMClient
        tracks = YMClient.rotor_station_tracks(station=self.station, queue=self.last_track).sequence
        self.iterator = 0
        self.listcount = len(tracks)
        Gdk.threads_add_idle(GLib.PRIORITY_DEFAULT_IDLE, self.add_entry, tracks)
        return False

    def add_entry(self, tracks):
        track = tracks[self.iterator].track
        if track.available:
            entry = RB.RhythmDBEntry.new(self.db, self.entry_type, str(track.id)+':'+str(track.albums[0].id))
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

GObject.type_register(YMLikesSource)

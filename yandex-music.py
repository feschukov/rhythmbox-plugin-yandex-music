from gi.repository import GObject, RB, Peas, Gio, GLib, Gdk, Gtk
from yandex_music import Client
from user_likes import YMLikesEntry, YMLikesSource
from rotor_stations_dashboard import YMDashboardEntry, YMDashboardSource
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
        self.login_yandex()
        self.entry_type = YMLikesEntry(self.client)
        db.register_entry_type(self.entry_type)
        iconfile = Gio.File.new_for_path(self.plugin_info.get_data_dir()+'/yandex-music.svg')
        self.source = GObject.new(YMLikesSource, shell=shell, name=_('Мне нравится'), entry_type=self.entry_type, plugin=self, icon=Gio.FileIcon.new(iconfile))
        self.source.setup(db, self.client)
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
        if self.client:
            dashboard = self.client.rotor_stations_dashboard()
            for result in dashboard.stations:
                entry_type = YMDashboardEntry(self.client, result.station.id.type+':'+result.station.id.tag)
                source = GObject.new(YMDashboardSource, shell=shell, name=result.station.name, entry_type=entry_type, plugin=self)
                source.setup(db, self.client, result.station.id.type+':'+result.station.id.tag)
                shell.register_entry_type_for_source(source, entry_type)
                shell.append_display_page(source, self.page_group)
        return False

    def login_yandex(self):
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
            self.client = Client(token).init()
            return True

    def generate_token(self, login, password):
        link_post = "https://oauth.yandex.com/token"
        user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36"
        client_id = "23cabbbdc6cd418abb4b39c32c41195d"
        client_secret = "53bc75238f0c4d08a118e51fe9203300"
        header = {
            "user-agent": user_agent
        }
        try:
            request_post = f"grant_type=password&client_id={client_id}&client_secret={client_secret}&username={login}&password={password}"
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

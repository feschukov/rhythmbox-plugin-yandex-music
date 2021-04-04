# Copyright © 2021 Sergey Feschukov <snfesh@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from gi.repository import GObject, RB, Peas, Gio, GLib, Gdk, Gtk
from yandex_music import Client

class YandexMusic(GObject.Object, Peas.Activatable):
    object = GObject.property(type=GObject.Object)

    def __init__(self):
        super(YandexMusic, self).__init__()

    def do_activate(self):
        print('Yandex.Music plugin activating')
        schema_source = Gio.SettingsSchemaSource.new_from_directory(self.plugin_info.get_data_dir(), Gio.SettingsSchemaSource.get_default(), False,)
        schema = schema_source.lookup('org.gnome.rhythmbox.plugins.yandex-music', False)
        self.settings = Gio.Settings.new_full(schema, None, None)
        shell = self.object
        db = shell.props.db
        page_group = RB.DisplayPageGroup(shell=shell, id='yandex-music-playlist', name=_('Яндекс')+'.'+_('Music'), category=RB.DisplayPageGroupCategory.TRANSIENT)
        shell.append_display_page(page_group, None)
        self.entry_type = YMEntryType()
        db.register_entry_type(self.entry_type)
        iconfile = Gio.File.new_for_path(self.plugin_info.get_data_dir()+'/yandex-music.svg')
        self.source = GObject.new(YMSource, shell=shell, name=_('Мне нравится'), entry_type=self.entry_type, plugin=self, icon=Gio.FileIcon.new(iconfile))
        self.source.setup(db, self.settings)
        shell.register_entry_type_for_source(self.source, self.entry_type)
        shell.append_display_page(self.source, page_group)

    def do_deactivate(self):
        print('Yandex.Music plugin deactivating')
        self.source.delete_thyself()
        self.source = None
        self.entry_type = None
        self.client = None
        self.settings = None

class YMEntryType(RB.RhythmDBEntryType):
    def __init__(self):
        RB.RhythmDBEntryType.__init__(self, name='ym-entry-type', save_to_disk=False)

    def do_get_playback_uri(self, entry):
        global YMClient
        track_id = entry.get_string(RB.RhythmDBPropType.LOCATION)
        downinfo = YMClient.tracks_download_info(track_id=track_id, get_direct_links=True)
        return downinfo[1].direct_link

class YMSource(RB.BrowserSource):
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
            if self.login_yandex():
                Gdk.threads_add_idle(GLib.PRIORITY_DEFAULT_IDLE, self.users_likes_tracks)

    def login_yandex(self):
        global YMClient
        token = self.settings.get_string('token')
        self.iterator = 0
        while len(token) < 1 and self.iterator < 5:
            d = Gtk.Dialog(buttons=(Gtk.STOCK_OK, Gtk.ResponseType.OK))
            label_login = Gtk.Label(_('Login'))
            label_passwd = Gtk.Label(_('Password'))
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
                token = Client.generate_token_by_username_and_password(login, password)
                if len(token) > 0:
                    self.settings.set_string('token', token)
            self.iterator += 1
        if len(token) < 1:
            return False
        else:
            YMClient = Client.from_token(token)
            return True

    def users_likes_tracks(self):
        global YMClient
        trackslist = YMClient.users_likes_tracks()
        tracks = trackslist.fetch_tracks()
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

GObject.type_register(YMSource)

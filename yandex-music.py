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

from gi.repository import GObject, RB, Peas, Gio
from yandex_music import Client

class YandexMusic(GObject.Object, Peas.Activatable):
    object = GObject.property(type=GObject.Object)

    def __init__(self):
        super(YandexMusic, self).__init__()

    def do_activate(self):
        shell = self.object
        db = shell.props.db
        self.entry_type = YMEntryType()
        db.register_entry_type(self.entry_type)
        self.client = Client.from_credentials('login@yandex.ru', 'password')
        iconfile = Gio.File.new_for_path(self.plugin_info.get_data_dir()+"/yandex-music.svg")
        self.source = GObject.new(YMSource, shell=shell, name=_("Yandex")+"."+_("Music"), entry_type=self.entry_type, plugin=self, icon=Gio.FileIcon.new(iconfile))
        self.source.setup(db, self.client)
        shell.register_entry_type_for_source(self.source, self.entry_type)
        group = RB.DisplayPageGroup.get_by_id("library")
        shell.append_display_page(self.source, group)

    def do_deactivate(self):
        self.source.delete_thyself()
        self.source = None
        self.entry_type = None
        self.client = None

class YMEntryType(RB.RhythmDBEntryType):
    def __init__(self):
        RB.RhythmDBEntryType.__init__(self, name='ym-entry-type', save_to_disk=False)

class YMSource(RB.BrowserSource):
    def __init__(self):
        RB.BrowserSource.__init__(self)

    def setup(self, db, client):
        self.initialised = False
        self.db = db
        self.entry_type = self.props.entry_type
        self.client = client

    def do_selected(self):
        if not self.initialised :
            self.initialised = True
            audios = self.client.users_likes_tracks()
            i = 1
            for audio in audios:
                track = audio.fetch_track()
                loadinfo = track.get_download_info(get_direct_links=True)
                entry = RB.RhythmDBEntry.new(self.db, self.entry_type, loadinfo[0].direct_link)
                self.db.commit()
                if entry is not None:
                    self.db.entry_set(entry, RB.RhythmDBPropType.TITLE, track.title)
                    self.db.entry_set(entry, RB.RhythmDBPropType.DURATION, track.duration_ms/1000)
                    self.db.entry_set(entry, RB.RhythmDBPropType.ARTIST, track.artists[0].name)
                    self.db.entry_set(entry, RB.RhythmDBPropType.ALBUM, track.albums[0].title)
                    #self.db.entry_set(entry, RB.RhythmDBPropType.IMAGE, track.albums[0].cover_uri)
                self.db.commit()
                i=i+1
                if i>5 :
                    break

GObject.type_register(YMSource)

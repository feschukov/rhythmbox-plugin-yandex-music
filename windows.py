from gi.repository import Gtk

class YMAuthWindow(Gtk.Dialog):
    res = {"login": None, "password": None}

    def __init__(self, parent):
        Gtk.Dialog.__init__(self, _('Яндекс.Музыка'), parent, 0, (Gtk.STOCK_OK, Gtk.ResponseType.OK, Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL))
        self.connect('response', self.on_response)
        window = self.get_content_area()

        login_hbox = Gtk.HBox()
        login_label = Gtk.Label(_('Логин'))
        self.entry_login = Gtk.Entry(width_chars=25, activates_default=True)
        login_hbox.pack_start(login_label, True, True, 10)
        login_hbox.pack_start(self.entry_login, True, True, 10)
        window.pack_start(login_hbox, True, True, 10)

        password_hbox = Gtk.HBox()
        password_label = Gtk.Label(_('Пароль'))
        self.entry_password = Gtk.Entry(width_chars=25, activates_default=True, visibility=False)
        password_hbox.pack_start(password_label, True, True, 10)
        password_hbox.pack_start(self.entry_password, True, True, 10)
        window.pack_start(password_hbox, True, True, 10)

        self.show_all()

    def on_response(self, widget, response_id):
        self.res['login'] = self.entry_login.get_text()
        self.res['password'] = self.entry_password.get_text()

    def get_result(self):
        return self.res

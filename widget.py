import requests
from gi.repository import GLib, Gtk, GdkPixbuf


class AuthDialog(Gtk.Dialog):
    res = {"code": None}

    def __init__(self, parent):
        Gtk.Dialog.__init__(self, _('Яндекс.Музыка'), parent, 0, (Gtk.STOCK_OK, Gtk.ResponseType.OK, Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL))
        self.connect('response', self.on_response)
        window = self.get_content_area()

        code_hbox = Gtk.HBox()
        code_label = Gtk.Label(_('Код подтверждения'))
        self.entry_code = Gtk.Entry(width_chars=7, activates_default=True)
        code_hbox.pack_start(code_label, True, True, 10)
        code_hbox.pack_start(self.entry_code, True, True, 10)
        window.pack_start(code_hbox, True, True, 10)

        self.show_all()

    def on_response(self, widget, response_id):
        self.res['code'] = self.entry_code.get_text()

    def get_result(self):
        return self.res

class CaptchaDialog(Gtk.Dialog):
    res = {"captcha_answer": None}

    def __init__(self, parent, captcha_url):
        Gtk.Dialog.__init__(self, _('Яндекс.Музыка'), parent, 0, (Gtk.STOCK_OK, Gtk.ResponseType.OK, Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL))
        self.connect('response', self.on_response)
        window = self.get_content_area()

        response = requests.get(captcha_url)
        content = response.content
        loader = GdkPixbuf.PixbufLoader()
        loader.write_bytes(GLib.Bytes.new(content))
        loader.close()

        captcha_hbox = Gtk.HBox()
        captcha_img = Gtk.Image.new_from_pixbuf(loader.get_pixbuf())
        captcha_hbox.pack_start(captcha_img, True, True, 10)
        window.pack_start(captcha_hbox, True, True, 10)

        captcha_answer_hbox = Gtk.HBox()
        captcha_answer_label = Gtk.Label(_('Ответ'))
        self.entry_captcha_answer = Gtk.Entry(width_chars=25, activates_default=True)
        captcha_answer_hbox.pack_start(captcha_answer_label, True, True, 10)
        captcha_answer_hbox.pack_start(self.entry_captcha_answer, True, True, 10)
        window.pack_start(captcha_answer_hbox, True, True, 10)

        self.show_all()

    def on_response(self, widget, response_id):
        self.res['captcha_answer'] = self.entry_captcha_answer.get_text()

    def get_result(self):
        return self.res

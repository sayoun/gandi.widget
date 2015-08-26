# -*- coding: utf-8 -*-

from gi.repository import Gtk, Gdk, GLib
from gi.repository import Notify


class Base(object):
    def __init__(self, widget):
        self._widget = widget

    def list(self):
        raise NotImplemented()

    def copy(self, widget, element):
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        clipboard.set_text(element, -1)
        message = '%s copied to clipboard' % element
        self._notify(message)

    def open_url(self, widget, address):
        Gtk.show_uri(None, address, Gdk.CURRENT_TIME)

    def _call_api(self, method, *args, **kwargs):
        try:
            method(*args, **kwargs)
        except Exception as err:
            print('Error: ', err.message)
            error_indicator = Gtk.ImageMenuItem.new_with_label(
                'An error occured.')
            img = Gtk.Image.new_from_icon_name("error", Gtk.IconSize.MENU)
            error_indicator.set_always_show_image(True)
            error_indicator.set_image(img)
            error_indicator.show()
            self._widget.menu.append(error_indicator)

    def _notify(self, message):
        notification = Notify.Notification.new(
            'Gandi Widget',
            message,
            'gandi-widget'
        )

        notification.set_hint('transient', GLib.Variant.new_boolean(True))
        notification.set_urgency(urgency=Notify.Urgency.CRITICAL)
        notification.set_timeout(1)
        notification.show()

    def _separator(self, sub_menu):
        separator = Gtk.SeparatorMenuItem.new()
        separator.show()
        sub_menu.append(separator)

    def _add_menuitem(self, sub_menu, label, action=None, attr=None, img=None):
        if img:
            item = Gtk.ImageMenuItem.new_with_label(label)
            item.set_always_show_image(True)
            item.set_image(img)
        else:
            item = Gtk.MenuItem.new()
            item.set_label(label)

        if action:
            item.connect('activate', action, *attr)

        item.show()
        if sub_menu:
            sub_menu.append(item)

        return item

    def _dialog(self, widget, title, text,
                callback_ok, callback_ko=None, callback_params=None):
        win = Gtk.MessageDialog(None,
                                Gtk.DialogFlags.MODAL,
                                Gtk.MessageType.INFO,
                                Gtk.ButtonsType.YES_NO,
                                text)
        win.set_title(title)
        win.connect('response', self._dialog_callback,
                    callback_ok, callback_ko, callback_params)
        win.run()
        win.hide()

    def _dialog_callback(self, widget, response,
                         callback_ok, callback_ko, callback_params):
        if response == Gtk.ResponseType.YES:
            callback_ok(*callback_params)
        elif response == Gtk.ResponseType.NO and callback_ko:
            callback_ko(*callback_params)

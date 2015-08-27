# -*- coding: utf-8 -*-

from gi.repository import Gtk

from gandi.cli.modules.paas import Paas as ApiPaas
from gandi.cli.modules.vhost import Vhost as ApiVhost

from .base import Base


class Paas(Base):

    @staticmethod
    def retrieve():
        instances = []
        for paas in ApiPaas.list({'state': 'running', 'sort_by': 'name'}):
            paas['vhosts'] = vhosts = ApiVhost.list({'paas_id': paas['id']})
            instances.append(paas)

        return instances

    def display(self, instances):
        # create a menu item per paas
        menu_items = []
        for paas in instances:
            name = paas['name']
            state = paas['state']
            paas_id = paas['id']

            if state == 'running':
                img = Gtk.Image.new_from_icon_name(Gtk.STOCK_YES,
                                                   Gtk.IconSize.MENU)
            else:
                img = Gtk.Image.new_from_icon_name(Gtk.STOCK_NO,
                                                   Gtk.IconSize.MENU)

            menu_item = self._add_menuitem(None, name, img=img)

            sub_menu = Gtk.Menu.new()

            self._add_menuitem(sub_menu, 'Type: %s' % paas['type'])
            self._add_menuitem(sub_menu, 'Size: %s' % paas['size'])
            self._add_menuitem(sub_menu, 'Console: %s' % paas['console'],
                               action=self.copy,
                               attr=(paas['console'],))

            self._separator(sub_menu)

            for host in paas['vhosts']:
                address = 'http%s://%s' % ('s' if host['cert_id'] else '',
                                           host['name'])
                self._add_menuitem(sub_menu, 'Vhost: %s' % host['name'],
                                   action=self.open_url,
                                   attr=(address,))

            self._separator(sub_menu)

            if state == "running":
                img = Gtk.Image.new_from_icon_name("system-shutdown",
                                                   Gtk.IconSize.MENU)
                self._add_menuitem(sub_menu, 'Stop...',
                                   action=self.on_power_toggled,
                                   attr=(name, 'stop'),
                                   img=img)

                img = Gtk.Image.new_from_icon_name("system-restart",
                                                   Gtk.IconSize.MENU)
                self._add_menuitem(sub_menu, 'Reboot...',
                                   action=self.on_power_toggled,
                                   attr=(name, 'reboot'),
                                   img=img)
            else:
                img = Gtk.Image.new_from_icon_name("gtk-ok",
                                                   Gtk.IconSize.MENU)
                self._add_menuitem(sub_menu, 'Start...',
                                   action=self.on_power_toggled,
                                   attr=(name, 'start'),
                                   img=img)

            self._separator(sub_menu)

            menu_item.set_submenu(sub_menu)
            menu_items.append(menu_item)

        return menu_items

    def on_power_toggled(self, widget, paas_name, action):
        if action == 'start':
            self._call_api(ApiPaas.start, paas_name, background=True)
        if action == 'stop':
            self._call_api(ApiPaas.stop, paas_name, background=True)
        if action == 'reboot':
            self._call_api(ApiPaas.reboot, paas_name, background=True)

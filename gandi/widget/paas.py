# -*- coding: utf-8 -*-

from gi.repository import Gtk

from gandi.cli.modules.paas import Paas as ApiPaas
from gandi.cli.modules.vhost import Vhost as ApiVhost

from .base import Base


class Paas(Base):

    def list(self):
        instances = ApiPaas.list()
        # create a menu item per paas
        menu_items = []
        for paas in instances:
            name = paas['name']
            state = paas['state']
            paas_id = paas['id']

            menu_item = Gtk.ImageMenuItem.new_with_label(name)
            menu_item.set_always_show_image(True)

            if state == "running":
                img = Gtk.Image.new_from_icon_name(Gtk.STOCK_YES,
                                                   Gtk.IconSize.MENU)
                menu_item.set_image(img)
            else:
                img = Gtk.Image.new_from_icon_name(Gtk.STOCK_NO,
                                                   Gtk.IconSize.MENU)
                menu_item.set_image(img)

            # show the item
            menu_item.show()

            # create the submenu for the paas
            sub_menu = Gtk.Menu.new()
            paas = ApiPaas.info(paas_id)

            type = Gtk.MenuItem.new()
            type.set_label('Type: %s' % paas['type'])
            type.show()
            sub_menu.append(type)

            size = Gtk.MenuItem.new()
            size.set_label('Size: %s' % paas['size'])
            size.show()
            sub_menu.append(size)

            console = Gtk.MenuItem.new()
            console.set_label('Console: %s' % paas['console'])
            console.connect('activate', self.copy, paas['console'])
            console.show()
            sub_menu.append(console)

            vhosts = ApiVhost.list({'paas_id': paas_id})
            for host in vhosts:
                address = 'http%s://%s' % ('s' if host['cert_id'] else '',
                                           host['name'])
                item_vhost = Gtk.MenuItem.new()
                item_vhost.set_label('Vhost: %s' % host['name'])
                item_vhost.connect('activate', self.open_url, address)
                item_vhost.show()
                sub_menu.append(item_vhost)

            if state == "running":
                power_off = Gtk.ImageMenuItem.new_with_label('Stop...')
                power_off.set_always_show_image(True)
                img = Gtk.Image.new_from_icon_name("system-shutdown",
                                                   Gtk.IconSize.MENU)
                power_off.set_image(img)
                power_off.connect('activate', self.on_power_toggled, name,
                                  'stop')
                power_off.show()
                sub_menu.append(power_off)

                reboot = Gtk.ImageMenuItem.new_with_label('Reboot...')
                reboot.set_always_show_image(True)
                img = Gtk.Image.new_from_icon_name("system-restart",
                                                   Gtk.IconSize.MENU)
                reboot.set_image(img)
                reboot.connect('activate', self.on_power_toggled, name,
                               'reboot')
                reboot.show()
                sub_menu.append(reboot)

            else:
                power_on = Gtk.ImageMenuItem.new_with_label('Start...')
                power_on.set_always_show_image(True)
                img = Gtk.Image.new_from_icon_name("gtk-ok",
                                                   Gtk.IconSize.MENU)
                power_on.set_image(img)
                power_on.connect('activate', self.on_power_toggled, name,
                                 'start')
                power_on.show()
                sub_menu.append(power_on)

            seperator = Gtk.SeparatorMenuItem.new()
            seperator.show()
            sub_menu.append(seperator)

            menu_item.set_submenu(sub_menu)
            menu_items.append(menu_item)

        return menu_items

    def on_power_toggled(self, widget, paas_name, action):
        try:
            if action == 'start':
                ApiPaas.start(paas_name, background=True)
            if action == 'stop':
                ApiPaas.stop(paas_name, background=True)
            if action == 'reboot':
                ApiPaas.reboot(paas_name, background=True)
        except Exception as err:
            print('Error: ', err.message)
            error_indicator = Gtk.ImageMenuItem.new_with_label(
                'An error occured.')
            img = Gtk.Image.new_from_icon_name("error", Gtk.IconSize.MENU)
            error_indicator.set_always_show_image(True)
            error_indicator.set_image(img)
            error_indicator.show()
            self._widget.menu.append(error_indicator)

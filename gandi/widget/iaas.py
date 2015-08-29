# -*- coding: utf-8 -*-

from gi.repository import Gtk, Gdk, GLib
from gi.repository import Notify

from gandi.cli.modules.iaas import Iaas as ApiIaas
from gandi.cli.modules.account import Account as ApiAccount

from .base import Base


class Iaas(Base):

    @staticmethod
    def retrieve():
        vms = []
        for vm in ApiIaas.list({'state': ['running', 'halted'],
                                          'sort_by': 'hostname'}):
            vms.append(ApiIaas.info(vm['id']))

        if hasattr(ApiAccount, 'all'):
            account = ApiAccount.all()
        else:
            account = ApiAccount.info()
            account['credit_usage'] = ApiAccount.creditusage()

        return [vms, account]

    def display(self, elements):
        vms, account = elements

        menu_items = []

        # add an account menu item
        menu_item = self._add_menuitem(None, 'Account')
        sub_menu = Gtk.Menu.new()
        self._add_menuitem(sub_menu, 'Credits : %s' % account['credits'])
        self._add_menuitem(sub_menu, 'Usage %s/h' %
                           account['credit_usage'])
        self._add_menuitem(sub_menu, 'Average cost : %s' %
                           account['average_credit_cost'])
        if 'left' in account:
            years, months, days, hours = account['left']
            left_str = ('%d year(s) %d month(s) %d day(s) %d hour(s)' %
                        (years, months, days, hours))
            self._add_menuitem(sub_menu, left_str)
        menu_item.set_submenu(sub_menu)
        menu_items.append(menu_item)

        # create a menu item per vm
        for vm in vms:
            hostname = vm['hostname']
            state = vm['state']
            vm_id = vm['id']

            if state == "running":
                img = Gtk.Image.new_from_icon_name(Gtk.STOCK_YES,
                                                   Gtk.IconSize.MENU)
            else:
                img = Gtk.Image.new_from_icon_name(Gtk.STOCK_NO,
                                                   Gtk.IconSize.MENU)

            menu_item = self._add_menuitem(None, hostname, img=img)

            # create the submenu for the vm
            sub_menu = Gtk.Menu.new()

            for iface in vm['ifaces']:
                for ip in iface['ips']:
                    ip_addr = ip['ip']
                    self._add_menuitem(sub_menu,
                                       'IP%d: %s' % (ip['version'], ip_addr),
                                       action=self.on_ip_clicked,
                                       attr=(ip_addr,))

            self._add_menuitem(sub_menu, 'Cores: %d' % vm['cores'])
            self._add_menuitem(sub_menu, 'Memory: %d' % vm['memory'])

            for disk in vm['disks']:
                self._separator(sub_menu)
                self._add_menuitem(sub_menu, 'Disk: %s' % disk['name'])

                if disk['label']:
                    self._add_menuitem(sub_menu, 'Label: %s' % disk['label'])

                if disk['kernel_version']:
                    self._add_menuitem(sub_menu,
                                       'Kernel: %s' % disk['kernel_version'])

                self._add_menuitem(sub_menu, 'Size: %s' % disk['size'])

            if state == "running":
                img = Gtk.Image.new_from_icon_name("system-shutdown",
                                                   Gtk.IconSize.MENU)
                self._add_menuitem(sub_menu, 'Stop...',
                                   action=self.on_power_toggled,
                                   attr=(hostname, 'stop'),
                                   img=img)

                img = Gtk.Image.new_from_icon_name("system-restart",
                                                   Gtk.IconSize.MENU)
                self._add_menuitem(sub_menu, 'Reboot...',
                                   action=self.on_power_toggled,
                                   attr=(hostname, 'reboot'),
                                   img=img)
            else:
                img = Gtk.Image.new_from_icon_name("gtk-ok",
                                                   Gtk.IconSize.MENU)
                self._add_menuitem(sub_menu, 'Start...',
                                   action=self.on_power_toggled,
                                   attr=(hostname, 'start'),
                                   img=img)

            self._separator(sub_menu)

            menu_item.set_submenu(sub_menu)
            menu_items.append(menu_item)
        return menu_items

    def on_ip_clicked(self, widget, address):
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        clipboard.set_text(address, -1)
        message = 'IP address %s copied to clipboard' % address
        self._notify(message)

    def on_power_toggled(self, widget, vm_hostname, action):
        if action == 'start':
            self._call_api(ApiIaas.start, vm_hostname, background=True)
        if action == 'stop':
            self._call_api(ApiIaas.stop, vm_hostname, background=True)
        if action == 'reboot':
            self._call_api(ApiIaas.reboot, vm_hostname, background=True)

# -*- coding: utf-8 -*-

from gi.repository import Gtk, Gdk, GLib
from gi.repository import Notify

from gandi.cli.modules.iaas import Iaas as ApiIaas


class Iaas(object):
    def __init__(self, widget):
        self._widget = widget

    def list(self):
        vms = ApiIaas.list()
        # create a menu item per vm
        menu_items = []
        for vm in vms:
            hostname = vm['hostname']
            state = vm['state']
            vm_id = vm['id']

            menu_item = Gtk.ImageMenuItem.new_with_label(hostname)
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

            # create the submenu for the vm
            sub_menu = Gtk.Menu.new()
            vm = ApiIaas.info(vm_id)

            for iface in vm['ifaces']:
                for ip in iface['ips']:
                    ip_addr = ip['ip']
                    item_ip = Gtk.MenuItem.new()
                    item_ip.set_label('IP%d: %s' % (ip['version'], ip_addr))
                    item_ip.connect('activate', self.on_ip_clicked, ip_addr)
                    item_ip.show()
                    sub_menu.append(item_ip)

            cores = Gtk.MenuItem.new()
            cores.set_label('Cores: %d' % vm['cores'])
            cores.show()
            sub_menu.append(cores)

            memory = Gtk.MenuItem.new()
            memory.set_label('Memory: %d' % vm['memory'])
            memory.show()
            sub_menu.append(memory)
            for disk in vm['disks']:
                seperator = Gtk.SeparatorMenuItem.new()
                seperator.show()
                sub_menu.append(seperator)

                item_disk_name = Gtk.MenuItem.new()
                item_disk_name.set_label('Disk: %s' % disk['name'])
                item_disk_name.show()
                sub_menu.append(item_disk_name)

                if disk['label']:
                    item_disk = Gtk.MenuItem.new()
                    item_disk.set_label('Label: %s' % disk['label'])
                    item_disk.show()
                    sub_menu.append(item_disk)

                if disk['kernel_version']:
                    item_disk = Gtk.MenuItem.new()
                    item_disk.set_label('Kernel: %s' % disk['kernel_version'])
                    item_disk.show()
                    sub_menu.append(item_disk)

                item_disk = Gtk.MenuItem.new()
                item_disk.set_label('Size: %s' % disk['size'])
                item_disk.show()
                sub_menu.append(item_disk)

            if state == "running":
                power_off = Gtk.ImageMenuItem.new_with_label('Stop...')
                power_off.set_always_show_image(True)
                img = Gtk.Image.new_from_icon_name("system-shutdown",
                                                   Gtk.IconSize.MENU)
                power_off.set_image(img)
                power_off.connect('activate', self.on_power_toggled, hostname,
                                  'stop')
                power_off.show()
                sub_menu.append(power_off)

                reboot = Gtk.ImageMenuItem.new_with_label('Reboot...')
                reboot.set_always_show_image(True)
                img = Gtk.Image.new_from_icon_name("system-restart",
                                                   Gtk.IconSize.MENU)
                reboot.set_image(img)
                reboot.connect('activate', self.on_power_toggled, hostname,
                               'reboot')
                reboot.show()
                sub_menu.append(reboot)

            else:
                power_on = Gtk.ImageMenuItem.new_with_label('Start...')
                power_on.set_always_show_image(True)
                img = Gtk.Image.new_from_icon_name("gtk-ok",
                                                   Gtk.IconSize.MENU)
                power_on.set_image(img)
                power_on.connect('activate', self.on_power_toggled, hostname,
                                 'start')
                power_on.show()
                sub_menu.append(power_on)

            seperator = Gtk.SeparatorMenuItem.new()
            seperator.show()
            sub_menu.append(seperator)

            menu_item.set_submenu(sub_menu)
            menu_items.append(menu_item)
        return menu_items

    def on_ip_clicked(self, widget, address):
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        clipboard.set_text(address, -1)
        message = 'IP address %s copied to clipboard' % address
        notification = Notify.Notification.new(
            'Gandi Widget',
            message,
            'gandi-widget'
        )

        notification.set_hint("transient", GLib.Variant.new_boolean(True))
        notification.set_urgency(urgency=Notify.Urgency.CRITICAL)
        notification.set_timeout(1)
        notification.show()

    def on_power_toggled(self, widget, vm_hostname, action):
        try:
            if action == 'start':
                ApiIaas.start(vm_hostname, background=True)
            if action == 'stop':
                ApiIaas.stop(vm_hostname, background=True)
            if action == 'reboot':
                ApiIaas.reboot(vm_hostname, background=True)
        except Exception as err:
            print('Error: ', err.message)
            error_indicator = Gtk.ImageMenuItem.new_with_label(
                'An error occured.')
            img = Gtk.Image.new_from_icon_name("error", Gtk.IconSize.MENU)
            error_indicator.set_always_show_image(True)
            error_indicator.set_image(img)
            error_indicator.show()
            self._widget.menu.append(error_indicator)

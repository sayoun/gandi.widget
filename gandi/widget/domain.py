# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

from gi.repository import Gtk, Gdk, GLib
from gi.repository import Notify

from gandi.cli.modules.domain import Domain as ApiDomain

from .base import Base


class Domain(Base):

    def list(self):
        domains = ApiDomain.list({})
        # create a menu item per domain
        menu_items = []
        for domain in domains:
            fqdn = domain['fqdn']

            menu_item = Gtk.ImageMenuItem.new_with_label(fqdn)
            menu_item.set_always_show_image(True)

            date_end = domain['date_delete']
            if date_end - datetime.now() > timedelta(days=30):
                img = Gtk.Image.new_from_icon_name(Gtk.STOCK_YES,
                                                   Gtk.IconSize.MENU)
            else:
                img = Gtk.Image.new_from_icon_name(Gtk.STOCK_YES,
                                                   Gtk.IconSize.MENU)
            menu_item.set_image(img)

            # show the item
            menu_item.show()

            # create the submenu for the domain
            sub_menu = Gtk.Menu.new()
            domain = ApiDomain.info(domain['fqdn'])

            # contacts
            for contact in ('owner', 'admin', 'bill', 'tech', 'reseller'):
                if domain['contacts'].get(contact):
                    handle = domain['contacts'][contact]['handle']
                    item_contact = Gtk.MenuItem.new()
                    item_contact.set_label('%s : %s' % (contact, handle))
                    item_contact.connect('activate', self.copy, handle)
                    item_contact.show()
                    sub_menu.append(item_contact)
            
            # seperator
            seperator = Gtk.SeparatorMenuItem.new()
            seperator.show()
            sub_menu.append(seperator)

            # autorenew
            label = 'active'
            method = self.deactivate_autorenew
            if not domain['autorenew']:
                label = 'inactive'
                method = self.activate_autorenew

            item_autorenew = Gtk.MenuItem.new()
            item_autorenew.set_label('Autorenew : %s' % label)
            item_autorenew.connect('activate', method, fqdn)
            item_autorenew.show()
            sub_menu.append(item_autorenew)

            # services
            item_services = Gtk.MenuItem.new()
            item_services.set_label('Services')
            item_services.show()
            sub_menu.append(item_services)

            services = Gtk.Menu.new()
            for service in domain.get('services', []):
                item_service = Gtk.MenuItem.new()
                item_service.set_label(service)
                item_service.show()
                services.append(item_service)

            item_services.set_submenu(services)

            # nameservers
            item_nameservers = Gtk.MenuItem.new()
            item_nameservers.set_label('Nameservers')
            item_nameservers.show()
            sub_menu.append(item_nameservers)

            nameservers = Gtk.Menu.new()
            for nameserver in domain.get('nameservers', []):
                item_nameserver = Gtk.MenuItem.new()
                item_nameserver.set_label(nameserver)
                item_nameserver.show()
                nameservers.append(item_nameserver)

            item_nameservers.set_submenu(nameservers)

            # seperator
            seperator = Gtk.SeparatorMenuItem.new()
            seperator.show()
            sub_menu.append(seperator)

            # renew
            renew = Gtk.ImageMenuItem.new_with_label('Renew...')
            renew.set_always_show_image(True)
            img = Gtk.Image.new_from_icon_name('go-jump',
                                               Gtk.IconSize.MENU)
            renew.set_image(img)
            renew.connect('activate', self.renew, fqdn)
            renew.show()
            sub_menu.append(renew)

            # add menu
            menu_item.set_submenu(sub_menu)
            menu_items.append(menu_item)
        return menu_items
            
    def deactivate_autorenew(self, widget, fqdn):
        self._notify('Deactivate autorenew for %s' % fqdn)
        self._call_api(ApiDomain.autorenew_deactivate, fqdn)

    def activate_autorenew(self, widget, fqdn):
        self._notify('Activate autorenew for %s' % fqdn)
        self._call_api(ApiDomain.autorenew_activate, fqdn)

    def renew(self, widget, fqdn):
        self._notify('Will start renew on %s' % fqdn)
        self._call_api(ApiDomain.renew, fqdn, 1, True)

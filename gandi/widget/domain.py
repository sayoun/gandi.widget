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

            date_end = domain['date_delete']
            if not date_end:
                img = Gtk.Image.new_from_icon_name(Gtk.STOCK_DISCARD,
                                                   Gtk.IconSize.MENU)
            elif date_end - datetime.now() > timedelta(days=30):
                img = Gtk.Image.new_from_icon_name(Gtk.STOCK_YES,
                                                   Gtk.IconSize.MENU)
            else:
                img = Gtk.Image.new_from_icon_name(Gtk.STOCK_NO,
                                                   Gtk.IconSize.MENU)

            menu_item = self._add_menuitem(None, fqdn, img=img)

            # create the submenu for the domain
            sub_menu = Gtk.Menu.new()
            domain = ApiDomain.info(domain['fqdn'])

            self._add_menuitem(sub_menu, 'Delete : %s' % domain['date_delete'])
            self._separator(sub_menu)

            # contacts
            for contact in ('owner', 'admin', 'bill', 'tech', 'reseller'):
                if domain['contacts'].get(contact):
                    handle = domain['contacts'][contact]['handle']
                    self._add_menuitem(sub_menu,
                                       '%s : %s' % (contact, handle),
                                       action=self.copy, attr=(handle,))
            
            # separator
            self._separator(sub_menu)

            # autorenew
            label = 'active'
            method = self.deactivate_autorenew
            if not domain['autorenew']:
                label = 'inactive'
                method = self.activate_autorenew

            self._add_menuitem(sub_menu, 'Autorenew : %s' % label,
                               action=method, attr=(fqdn,))

            # services
            item_services = self._add_menuitem(sub_menu, 'Services')

            services = Gtk.Menu.new()
            for service in domain.get('services', []):
                self._add_menuitem(services, service)

            item_services.set_submenu(services)

            # nameservers
            item_nameservers = self._add_menuitem(sub_menu, 'Nameservers')

            nameservers = Gtk.Menu.new()
            for nameserver in domain.get('nameservers', []):
                self._add_menuitem(nameservers, nameserver)

            item_nameservers.set_submenu(nameservers)

            # separator
            self._separator(sub_menu)

            # renew
            img = Gtk.Image.new_from_icon_name('go-jump',
                                               Gtk.IconSize.MENU)
            self._add_menuitem(sub_menu, 'Renew...',
                               action=self.renew, attr=(fqdn,),
                               img=img)

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

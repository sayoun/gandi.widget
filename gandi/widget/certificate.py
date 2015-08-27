# -*- coding: utf-8 -*-

import os
from datetime import datetime, timedelta

from gi.repository import Gtk, Gdk, GLib
from gi.repository import Notify

from gandi.cli.modules.cert import Certificate as ApiCert

from .base import Base

_curr_dir = os.path.split(__file__)[0]


class Certificate(Base):
    
    _icons = {'std': 'ssl_01_standard_small.png',
              'pro': 'ssl_02_pro_small.png',
              'bus': 'ssl_03_business_small.png'}

    @staticmethod
    def retrieve():
        return ApiCert.list({'status': 'valid', 'sort_by': 'cn'})

    def display(self, certs):
        # create a menu item per certificate
        menu_items = []
        for cert in certs:
            cn = cert['cn']
            _, type_, nb, _, _ = cert['package'].split('_')

            path = os.path.join(_curr_dir, 'resources', self._icons.get(type_))
            img = Gtk.Image()
            img.set_from_file(path)

            menu_item = self._add_menuitem(None, cn, img=img)

            # create the submenu for the cert
            sub_menu = Gtk.Menu.new()

            if cert['altnames']:
                item_alt = self._add_menuitem(sub_menu, 'Altnames')

                altnames = Gtk.Menu.new()
                for alt in cert['altnames']:
                    self._add_menuitem(altnames, alt)

                item_alt.set_submenu(altnames)

                self._separator(sub_menu)

            # display usefull dates
            self._add_menuitem(sub_menu, 'Start : %s' % cert['date_start'])
            self._add_menuitem(sub_menu, 'End : %s' % cert['date_end'])

            # display crt
            if cert['cert']:
                self._separator(sub_menu)

                self._add_menuitem(sub_menu, 'Copy CRT',
                                   action=self.copy, attr=(cert['cert'],))

            # add menu
            menu_item.set_submenu(sub_menu)
            menu_items.append(menu_item)
        return menu_items

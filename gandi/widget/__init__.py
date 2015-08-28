#!/usr/bin/env python

from functools import partial
import multiprocessing
import os

from gi.repository import Gtk, GLib
from gi.repository import AppIndicator3 as appindicator
from gi.repository import Notify

from gandi.cli.modules.status import Status
from gandi.cli.core.conf import GandiConfig

from .base import Base
from .certificate import Certificate
from .iaas import Iaas
from .domain import Domain
from .paas import Paas


_curr_dir = os.path.split(__file__)[0]


def get_iaas():
    return Iaas.retrieve()


def get_paas():
    return Paas.retrieve()


def get_domain():
    return Domain.retrieve()


def get_cert():
    return Certificate.retrieve()


class GandiWidget(Base):
    _subs = (('iaas', 'Server (IaaS)', get_iaas),
             ('paas', 'Instance (PaaS)', get_paas),
             ('domain', 'Domain', get_domain),
             ('cert', 'Certificate', get_cert),
            )
    _display = {'iaas': Iaas,
                'paas': Paas,
                'domain': Domain,
                'cert': Certificate}
    _menu = {}

    def __init__(self):
        self.indicator = appindicator.Indicator.new(
            "gandi.widget",
            "gandi.widget",
            appindicator.IndicatorCategory.APPLICATION_STATUS)

        self.indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
        self.icon = os.path.join(_curr_dir, 'resources', 'gandi.png')
        self.icon_err = os.path.join(_curr_dir, 'resources', 'gandi-err.png')
        self.indicator.set_icon(self.icon)

        self.queue = multiprocessing.Queue()
        self.pool = multiprocessing.Pool(1)

        Notify.init('Gandi Widget')

        GandiConfig.load_config()
        self.conf = GandiConfig.get('widget') or {}
        self.sections = self.conf.get('sections') or ['iaas', 'paas', 'domain']
        refresh = self.conf.get('refresh') or 60
        status_refresh = self.conf.get('status_refresh') or 20

        # create a menu
        self.menu = Gtk.Menu()
        # Add items to Menu and connect signals.
        self.build_menu()
        # Refresh menu every 1 min by default
        GLib.timeout_add_seconds(refresh, self.on_refresh)
        # Poll for status new events
        GLib.timeout_add_seconds(status_refresh, self.on_status_refresh)
        # Display elements
        GLib.timeout_add_seconds(10, self.display_elements)

    def _retrieve_all(self):
        for name, _, call_list in self._subs:
            if name not in self.sections:
                continue

            cb_menu = partial(self._retrieve_in_queue, name=name, queue=self.queue)
            self.pool.apply_async(call_list, callback=cb_menu)
        return True

    def build_menu(self):
        for name, label, _ in self._subs:
            if name not in self.sections:
                continue

            menu_item = self._add_menuitem(self.menu, label)
            menu_item.hide()

            sub_menu = Gtk.Menu.new()
            self._menu[name] = [menu_item, sub_menu]

            menu_item.set_submenu(sub_menu)

        self._separator(self.menu)
        self._add_menuitem(self.menu, 'Refresh', self.on_refresh, {})
        self._add_menuitem(self.menu, 'Quit', self.on_exit_activate, {})

        self.menu.show()
        self.indicator.set_menu(self.menu)

        self._retrieve_all()

    @staticmethod
    def _retrieve_in_queue(elements, name, queue):
        queue.put([name, elements])

    def display_elements(self):
        while not self.queue.empty():
            name, elements = self.queue.get()
            menu_item, sub_menu = self._menu[name]

            if not elements:
                menu_item.hide()
                continue

            for item in sub_menu.get_children():
                sub_menu.remove(item)

            for item in self._display[name](self).display(elements):
                sub_menu.append(item)

            menu_item.show()

        return True

    def on_refresh(self, widget=None):
        return self._retrieve_all()

    def on_status_refresh(self, widget=None):
        filters = {
            'category': 'Incident',
            'current': True,
        }
        events = Status.events(filters)
        for event in events:
            message = '%s: %s' % (','.join(event['services']), event['title'])

            self._notify(message, 'Gandi Status Event')

        if events:
            self.indicator.set_icon(self.icon_err)
        else:
            self.indicator.set_icon(self.icon)
        return True

    def on_exit_activate(self, widget):
        self.on_destroy(widget)

    def on_destroy(self, widget, data=None):
        Gtk.main_quit()


if __name__ == "__main__":
    # create the widget menu
    GandiWidget()
    # run the widget
    Gtk.main()

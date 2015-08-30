# -*- coding: utf-8 -*-

from gi.repository import Gtk, Gdk, GLib
from gi.repository import Notify

from gandi.cli.modules.oper import Oper as ApiOper

from .base import Base


class Oper(Base):

    @staticmethod
    def retrieve():
        if hasattr(ApiOper, 'count'):
            wait = ApiOper.count({'step': 'WAIT'})
            run = ApiOper.count({'step': 'RUN'})
            error = ApiOper.count({'step': 'ERROR'})
        else:
            wait = len(ApiOper.list({'step': 'WAIT'}))
            run = len(ApiOper.list({'step': 'RUN'}))
            error = len(ApiOper.list({'step': 'ERROR'}))
        return {'wait': wait, 'run': run, 'error': error}

    def label(self, opers):
        label = 'Op : wait=%(wait)s run=%(run)s error=%(error)s' % opers
        return label

    def icon(self, opers):
        if opers['error']:
            return Gtk.Image.new_from_icon_name(Gtk.STOCK_NO,
                                                Gtk.IconSize.MENU)
        return Gtk.Image.new_from_icon_name(Gtk.STOCK_YES,
                                            Gtk.IconSize.MENU)
        
    def display(self, opers):
        return []

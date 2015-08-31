# -*- coding: utf-8 -*-

from gi.repository import Gtk, Gdk, GLib
from gi.repository import Notify

from gandi.cli.modules.oper import Oper as ApiOper

from .base import Base


class Oper(Base):

    @staticmethod
    def retrieve():
        if hasattr(ApiOper, 'count'):
            cur = ApiOper.count({'step': ['BILL', 'WAIT', 'RUN', 'SUPPORT']})
            error = ApiOper.count({'step': 'ERROR'})
        else:
            cur = len(ApiOper.list({'step': ['BILL', 'WAIT', 'RUN',
                                             'SUPPORT']}))
            error = len(ApiOper.list({'step': 'ERROR'}))
        return {'cur': cur, 'error': error}

    def label(self, opers):
        label = 'Operation (cur=%(cur)s/error=%(error)s)' % opers
        return label

    def icon(self, opers):
        if opers['error']:
            return Gtk.Image.new_from_icon_name(Gtk.STOCK_NO,
                                                Gtk.IconSize.MENU)
        return Gtk.Image.new_from_icon_name(Gtk.STOCK_YES,
                                            Gtk.IconSize.MENU)
        
    def display(self, opers):
        return []

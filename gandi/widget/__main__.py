#!/usr/bin/python
# -*- coding: utf-8 -*-

from gandi.widget import GandiWidget
from gi.repository import Gtk


def main():
    # create the widget menu
    GandiWidget()
    # run the widget
    Gtk.main()


if __name__ == "__main__":
    main()

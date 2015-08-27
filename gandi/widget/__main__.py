#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
GandiWidget will read in gandi.cli configuration
~/.config/gandi/config.yaml

You can add a section :
widget:
    sections:
        - iaas
        - paas
        - domain
        - cert
    refresh: 60
    status_refresh: 20

"""


from gandi.widget import GandiWidget
from gi.repository import Gtk


def main():
    # create the widget menu
    GandiWidget()
    # run the widget
    Gtk.main()


if __name__ == "__main__":
    main()

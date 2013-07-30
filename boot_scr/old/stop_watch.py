!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Nifty GTK stopwatch using pygtk and gobject.
# min:sec.msec display; start, stop, reset and quit buttons.
#
# Version: 1.1
# Requires: python >=2.5, python-gtk2, python-gobject
#
# Version History:
# 1.0 - Initial Release
# 1.1 - PEP 8
#
# Copyright (C) 2009-2012 Jonas Wagner wagnercode@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import pygtk
import gtk
import pango
pygtk.require('2.0')
import gobject
gobject.threads_init()


class Stopwatch():
    def __init__(self):
        self.s = 0.0
        self.m = 0
        self.g_id = 0
        self.win()

    def b_start_cb(self, widget):
        # Start gobject, impossible to speed up by clicking multiple times
        if self.g_id == 0:
            self.g_id = gobject.timeout_add(100, self.count)

    def b_stop_cb(self, widget):
        # Kill gobject, reset g_id
        if self.g_id != 0:
            gobject.source_remove(self.g_id)
            self.g_id = 0

    def b_reset_cb(self, widget):
        # Reset time
        self.s = 0.0
        self.m = 0
        self.l_time.set_text("00:00.0")

    def win(self):
        win = gtk.Window(gtk.WINDOW_TOPLEVEL)
        win.connect("destroy", lambda q: gtk.main_quit())
        win.set_title("Stopwatch")
        win.set_border_width(20)

        # Table and window size
        table = gtk.Table(2, 3, False)
        win.set_geometry_hints(table, min_width=160, min_height=150)
        table.set_row_spacings(5)
        table.set_col_spacings(3)
        win.add(table)

        # AspectFrame, into table
        af_time = gtk.AspectFrame()
        table.attach(af_time, 0, 2, 0, 1)

        # Time label, into aspect frame, font size: 19
        self.l_time = gtk.Label("00:00.0")
        self.l_time.modify_font(pango.FontDescription("19"))
        af_time.add(self.l_time)

        # Buttons, into table, font size: 11
        b_start = gtk.Button("Start")
        b_start.child.modify_font(pango.FontDescription("11"))
        table.attach(b_start, 0, 1, 1, 2)
        b_start.connect("clicked", self.b_start_cb)

        b_stop = gtk.Button("Stop")
        b_stop.child.modify_font(pango.FontDescription("11"))
        table.attach(b_stop, 1, 2, 1, 2)
        b_stop.connect("clicked", self.b_stop_cb)

        b_reset = gtk.Button("Reset")
        b_reset.child.modify_font(pango.FontDescription("11"))
        table.attach(b_reset, 0, 1, 2, 3)
        b_reset.connect("clicked", self.b_reset_cb)

        b_quit = gtk.Button(" Quit ")
        b_quit.child.modify_font(pango.FontDescription("11"))
        table.attach(b_quit, 1, 2, 2, 3)
        b_quit.connect("clicked", lambda q: gtk.main_quit())

        # Run GTK and show window, buttons, etc.
        win.show_all()
        gtk.main()

    def count(self):
        # A minute yet?
        if self.s > 60:
            self.m += 1
            self.s = 0.0
        else:
            self.s += 0.1

        # Set new time to label
        self.l_time.set_text("%02i:%04.1f" % (self.m, self.s))

        # Play it again, Sam
        return True


if __name__ == "__main__":
    t = Stopwatch()

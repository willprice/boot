#!/usr/bin/env python
#
#      TestVirtualTerminal.py
#
#      Copyright 2007 Edward Andrew Robinson <earobinson@gmail>
#
#      This program is free software; you can redistribute it and/or modify
#      it under the terms of the GNU General Public License as published by
#      the Free Software Foundation; either version 2 of the License, or
#      (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public License for more details.
#
#      You should have received a copy of the GNU General Public License
#      along with this program; if not, write to the Free Software
#      Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#

import gtk

from VirtualTerminal import VirtualTerminal

class mainWindow(gtk.Window):
    def __init__(self):
        gtk.Window.__init__(self)
        self.connect('destroy', lambda w: gtk.main_quit())
        self.set_default_size(400, 400)

        self.button = gtk.Button('press me')
        self.button.connect("clicked", self.pressed_callback)

        self.command_entry = gtk.Entry()
        self.command_entry.set_text('python count.py')
        #self.command_entry.set_text('sudo aptitude install gaim-encryption')

        vbox = gtk.VBox()

        self.r = 0

        self.add(vbox)

        vbox.pack_start(self.command_entry, False)
        vbox.pack_start(self.button, True)

        self.myTerminal = terminal()

        self.show_all()

        gtk.main()

    def pressed_callback(self, button):
        print 'presed'
        column,row = self.myTerminal.terminal.get_cursor_position()
        if self.r != row:
            off = row-self.r
            text = self.myTerminal.terminal.get_text_range(row-off,0,row-1,-1,self.capture_text)
            self.r=row
            text = text.strip()
            print text
        self.button.set_sensitive(False)
        self.myTerminal.terminal.run_command(self.command_entry.get_text())
        self.button.set_sensitive(True)
        print 'done'

    def capture_text(self,text,text2,text3,text4):
        return True

class terminal(gtk.Window):
    def __init__(self):
        gtk.Window.__init__(self)
        #self.set_title(self.settings.application_name)
        self.connect('destroy', lambda w: gtk.main_quit())

        self.terminal = VirtualTerminal()

        #self.child_pid = self.terminal.fork_command()

        self.add(self.terminal)
        self.show_all()

mainWindow()

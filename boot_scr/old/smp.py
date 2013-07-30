#!/usr/bin/env python
#-*- coding:utf-8 -*-

import gtk, webkit, httplib, sys, os, thread, time

# set of methods
def delete_event(widget, event, data=None):
    return False

def destroy(widget, data=None):
    gtk.main_quit()

win = gtk.Window(gtk.WINDOW_TOPLEVEL)
win.connect("delete_event", delete_event)
win.connect("destroy", destroy)
win.set_resizable(True)
hlp_vbox = gtk.VBox()

txtview = gtk.TextView()
txtview.set_editable(True)
scroller = gtk.ScrolledWindow()
scroller.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
scroller.add(txtview)



# put stuff together
hlp_vbox.pack_start(scroller,True, True)

win.add(hlp_vbox)
textbuffer = txtview.get_buffer()

textbuffer.set_text('test ! erw rwe rw er wer werwerwerwerwerwerwerw erwer \n rwrwe \n erwer')

textbuffer.set_text('boh !')

win.show_all()



gtk.main()



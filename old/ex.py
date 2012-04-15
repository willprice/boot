#!/usr/bin/env python

import os, stat, gtk

def make_dev_layout():

    # device data
    dev_family  = ['spartan', 'stratix', 'fringe'] 
    dev_device  = ['xx', 'yy']
    dev_package = ['aa', 'bb']

    img = gtk.icon_theme_get_default().load_icon("document", gtk.ICON_SIZE_MENU, 0)
    # create an array of gtk.trees
    store = []
    for x in range(3):
        store.append(gtk.TreeStore(gtk.gdk.Pixbuf, str))

    # fill up the array of trees with data
    for x in dev_family:
        store[0].append(None, [img, x])
    for x in dev_device:
        store[1].append(None, [img, x])
    for x in dev_package:
        store[2].append(None, [img, x])

    # let's join all trees in one single layout
    layout = gtk.HBox(spacing=5)
    layout.pack_start(gtk.Label('Device type: '), False)
    for x in range(3):
        combo = gtk.ComboBox(store[x])
        combo_cell_text = gtk.CellRendererText()
        combo_cell_img = gtk.CellRendererPixbuf()
        combo.pack_start(combo_cell_img, False)
        combo.pack_start(combo_cell_text, True)
        combo.add_attribute(combo_cell_img, "pixbuf", 0)
        combo.add_attribute(combo_cell_text, "text", 1)
        layout.pack_start(combo, False)
    return layout

def layout_changed(self, widget):
    print 'ha'
    return 0


# put all together
window = gtk.Window()
window.connect("destroy", gtk.main_quit)
layout = make_dev_layout()
#layout.connect("clicked", layout_changed)
vbox = gtk.VBox(0)
vbox.pack_start(layout, False, False, 10)
window.add(vbox)
window.show_all()

gtk.main()


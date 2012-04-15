#!/usr/bin/env python

import os, stat, gtk

def make_dropdown_menu(data_in):

    # create a gtk.trees
    img = gtk.icon_theme_get_default().load_icon("document", gtk.ICON_SIZE_MENU, 0)
    store = gtk.TreeStore(gtk.gdk.Pixbuf, str)

    # fill up the tree with data
    for x in data_in:
        store.append(None, [img, x])

    # let's join all trees in one single layout
    combo = gtk.ComboBox(store)
    combo_cell_text = gtk.CellRendererText()
    combo_cell_img = gtk.CellRendererPixbuf()
    combo.pack_start(combo_cell_img, False)
    combo.pack_start(combo_cell_text, True)
    combo.add_attribute(combo_cell_img, "pixbuf", 0)
    combo.add_attribute(combo_cell_text, "text", 1)
    return combo

def device_changed(self, widget):
    print 'ha'
    return 0

# device data
dev_family  = ['spartan', 'stratix', 'fringe'] 
dev_device  = ['xx', 'yy']
dev_package = ['aa', 'bb']

# put all together
window = gtk.Window()
window.connect("destroy", gtk.main_quit)
#layout.connect("clicked", layout_changed)
vbox = gtk.VBox(0)
hbox = gtk.HBox(0)
vbox.pack_start(hbox, False, False, 10)
hbox.pack_start(gtk.Label('Device (family, device, package): '), False, False, 5)
a=make_dropdown_menu(dev_family)
b=make_dropdown_menu(dev_device)
c=make_dropdown_menu(dev_package)
hbox.pack_start(a, False, False, 5)
hbox.pack_start(b, False, False, 5)
hbox.pack_start(c, False, False, 5)
a.connect("changed", device_changed, a)
b.connect("changed", device_changed, b)
c.connect("changed", device_changed, c)
window.add(vbox)
window.show_all()

gtk.main()


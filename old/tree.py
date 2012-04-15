#!/usr/bin/env python

import os, stat, gtk

PATH = "./"
store = gtk.TreeStore(str, gtk.gdk.Pixbuf, int, bool)

def dirwalk(path, parent=None):
  for f in os.listdir(path):
    if ".pyc" not in f and not f.startswith("."):
      fullname = os.path.join(path, f)
      fdata = os.stat(fullname)
      is_folder = stat.S_ISDIR(fdata.st_mode)
      img = gtk.icon_theme_get_default().load_icon(
          "folder" if is_folder else "document",
          gtk.ICON_SIZE_MENU, 0)
      li = store.append(parent, [f, img, fdata.st_size, is_folder])
      if is_folder: dirwalk(fullname, li)

dirwalk(PATH)

combo_store = store.filter_new()
combo_store.set_visible_func(lambda model, iter: model[iter][3])

#combo = gtk.ComboBox(combo_store)
combo = gtk.ComboBox(store)
combo_cell_text = gtk.CellRendererText()
combo_cell_img = gtk.CellRendererPixbuf()
combo.pack_start(combo_cell_img, False)
combo.pack_start(combo_cell_text, True)
combo.add_attribute(combo_cell_img, "pixbuf", 1)
combo.add_attribute(combo_cell_text, "text", 0)

col = gtk.TreeViewColumn("File")
col_cell_text = gtk.CellRendererText()
col_cell_img = gtk.CellRendererPixbuf()
col.pack_start(col_cell_img, False)
col.pack_start(col_cell_text, True)
col.add_attribute(col_cell_text, "text", 0)
col.add_attribute(col_cell_img, "pixbuf", 1)

col2 = gtk.TreeViewColumn("Size")
col2_cell_text = gtk.CellRendererText()
col2.pack_start(col2_cell_text)
col2.add_attribute(col2_cell_text, "text", 2)

tree = gtk.TreeView(store)
tree.append_column(col)
tree.append_column(col2)

scroll = gtk.ScrolledWindow()
scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
scroll.add(tree)

completion = gtk.EntryCompletion()
completion_img = gtk.CellRendererPixbuf()
completion.set_model(store)
completion.pack_start(completion_img)
completion.add_attribute(completion_img, "pixbuf", 1)
completion.set_text_column(0)

entry = gtk.Entry()
entry.set_completion(completion)

layout = gtk.VBox(spacing=5)
#layout.pack_start(entry, False)
layout.pack_start(combo, False)
#layout.pack_start(scroll, True, True)

window = gtk.Window()
window.connect("destroy", gtk.main_quit)
window.add(layout)
window.show_all()

gtk.main()


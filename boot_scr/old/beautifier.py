#!/usr/bin/env python

# http://python.zirael.org/e-gtk-textview2.html

# ensure that PyGTK 2.0 is loaded - not an older version
import pygtk
pygtk.require('2.0')
# import the GTK module
import gtk
import pango #@+

class MyGUI:

  def __init__( self, title):
    self.window = gtk.Window()
    self.title = title
    self.window.set_title( title)
    self.window.set_size_request( -1, 300)
    self.window.connect( "destroy", self.destroy)
    self.create_interior()
    self.window.show_all()

  def create_interior( self):
    self.mainbox = gtk.VBox()
    self.window.add( self.mainbox)
    # the textview
    self.textview = gtk.TextView()
    self.textbuffer = self.textview.get_buffer()
    self.mainbox.pack_start( self.textview)
    self.textview.show()
    # fill the text buffer
    # heading
    h_tag = self.textbuffer.create_tag( "h", size_points=16, weight=pango.WEIGHT_BOLD) #@+
    position = self.textbuffer.get_end_iter()
    self.textbuffer.insert_with_tags( position, "Heading\n", h_tag) #@+
    # normal text
    position = self.textbuffer.get_end_iter()
    self.textbuffer.insert( position, "Several lines\nof normal text.\n") #@+
    # more text
    position = self.textbuffer.get_end_iter()
    i_tag = self.textbuffer.create_tag( "i", style=pango.STYLE_ITALIC) #@+
    self.textbuffer.insert_with_tags( position, "italic text", i_tag) #@+
    position = self.textbuffer.get_end_iter()
    self.textbuffer.insert_with_tags( position, " combined with heading", i_tag, h_tag) #@+
    position = self.textbuffer.get_end_iter()
    c_tag = self.textbuffer.create_tag( "colored", foreground="#FFFF00", background="#0000FF") #@+
    self.textbuffer.insert_with_tags( position, "\nand color", i_tag, h_tag, c_tag) #@+
    e_tag = self.textbuffer.create_tag( "fixed", editable=False) #@+
    position = self.textbuffer.get_end_iter()
    self.textbuffer.insert_with_tags( position, "\nnon-editable ", e_tag) #@+
    position = self.textbuffer.get_end_iter()    
    self.textbuffer.insert_with_tags_by_name( position, " and colored text", "colored", "fixed") #@+
    # show the box
    self.mainbox.show()

  def main( self):
    gtk.main()

  def destroy( self, w):
    gtk.main_quit()

if __name__ == "__main__":
  m = MyGUI( "TextView example II.")
  m.main()

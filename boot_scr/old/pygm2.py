#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    GTKPygments
    ~~~~~~~~~~~

    proof of concept pygments to gtk widget renderer

    :copyright: 2007 by Armin Ronacher.
    :license: GNU GPL.
"""
import pygtk
pygtk.require('2.0')
import gtk
import pango
from pygments.lexers import PythonLexer
from pygments.styles.tango import TangoStyle


f = file(__file__)
try:
    SOURCE = f.read()
finally:
    f.close()

class GTKPygments(gtk.Window):
    def __init__(self):
        super(GTKPygments, self).__init__()
        self.set_title('GTK Pygments')

        self.STYLE = TangoStyle


        win = gtk.ScrolledWindow()
        self.add(win)
        self.textview = gtk.TextView()
        win.add(self.textview)
        self.buf = gtk.TextBuffer()

        self.PrettyText(self)

        self.connect('delete-event', lambda *a: gtk.main_quit())
        self.buf.connect('changed', self.txt_changed)

        self.textview.set_buffer(self.buf)
        self.textview.set_editable(True)
        self.textview.modify_font(pango.FontDescription('monospace'))

        self.resize(800, 500)
        self.show_all()


    def PrettyText(self,widget):
        self._txt = SOURCE
        styles = {}

        for token, value in PythonLexer().get_tokens(self._txt):
            while not self.STYLE.styles_token(token) and token.parent:
                token = token.parent
            if token not in styles:
                styles[token] = self.buf.create_tag()
            start = self.buf.get_end_iter()
            self.buf.insert_with_tags(start, value.encode('utf-8'), styles[token])
        
        for token, tag in styles.iteritems():
            self.style = self.STYLE.style_for_token(token)
            if self.style['bgcolor']:
                tag.set_property('background', '#' + self.style['bgcolor'])
            if self.style['color']:
                tag.set_property('foreground', '#' + self.style['color'])
            if self.style['bold']:
                tag.set_property('weight', pango.WEIGHT_BOLD)
            if self.style['italic']:
                tag.set_property('style', pango.STYLE_ITALIC)
            if self.style['underline']:
                tag.set_property('underline', pango.UNDERLINE_SINGLE)
    
    

    def txt_changed(self,widget,prettyWin):
        print 'bingo'




    def run(self):
        gtk.main()


if __name__ == '__main__':
    GTKPygments().run()

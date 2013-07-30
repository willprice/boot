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
from pygments.styles.colorful import ColorfulStyle

from pygments.token import Name, Keyword


f = file(__file__)
try:
    SOURCE = f.read()
finally:
    f.close()

class MyPythonLexer(PythonLexer):
    EXTRA_KEYWORDS = ['pango', 'EXTRA_KEYWORDS', 'foobar', 'barfoo', 'spam', 'eggs']

    def get_tokens_unprocessed(self, text):
        for index, token, value in PythonLexer.get_tokens_unprocessed(self, text):
            if token is Name and value in self.EXTRA_KEYWORDS:
                yield index, Keyword.Pseudo, value
            else:
                yield index, token, value


def beautify(buf,SOURCE):
    STYLE = ColorfulStyle
    styles = {}
    #for token, value in PythonLexer().get_tokens(SOURCE):
    for token, value in MyPythonLexer().get_tokens(SOURCE):
        while not STYLE.styles_token(token) and token.parent:
            token = token.parent
        if token not in styles:
            styles[token] = buf.create_tag()
        start = buf.get_end_iter()
        buf.insert_with_tags(start, value.encode('utf-8'), styles[token])
    

    for token, tag in styles.iteritems():
        style = STYLE.style_for_token(token)
        if style['bgcolor']:
            tag.set_property('background', '#' + style['bgcolor'])
        if style['color']:
            tag.set_property('foreground', '#' + style['color'])
        if style['bold']:
            tag.set_property('weight', pango.WEIGHT_BOLD)
        if style['italic']:
            tag.set_property('style', pango.STYLE_ITALIC)
        if style['underline']:
            tag.set_property('underline', pango.UNDERLINE_SINGLE)
    #print style
    return 0


class GTKPygments(gtk.Window):

    def __init__(self):
        super(GTKPygments, self).__init__()
        self.set_title('GTK Pygments')

        win = gtk.ScrolledWindow()
        self.add(win)
        self.textview = gtk.TextView()
        win.add(self.textview)
        buf = gtk.TextBuffer()

        beautify(buf,SOURCE)

        self.connect('delete-event', lambda *a: gtk.main_quit())

        self.textview.set_buffer(buf)
        self.textview.set_editable(True)
        self.textview.modify_font(pango.FontDescription('monospace'))

        self.resize(800, 500)
        self.show_all()


    def run(self):
        gtk.main()


if __name__ == '__main__':
    GTKPygments().run()

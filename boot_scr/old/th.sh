
# Copyright (c) 2005 Antoon Pardon
# 
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import pygtk
pygtk.require('2.0')

import gtk
import gtk.gdk as gdk
import pango

from threading import Thread, Lock
from thread import error as thread_error

from random import Random, randint, sample
from time import sleep, time

import os
import sys

pname = sys.argv.pop(0).split(os.sep)[-1]
demo_id = pname.split('.')[0].replace("demo", '')

converters = [int, float]
arguments  = [20, 0.0]

for i in range(min(len(arguments), len(sys.argv))):
  try:
    arguments[i] = converters[i](sys.argv[i])
  except ValueError:
    pass

#print arguments
max_count, sleep_time = arguments

class Counting (Thread):

  def __init__(self, Id):
    self.Id = Id
    self.ctrl = True
    self.Running = False
    self.ShowMode = 0
    self.Time = 0
    self.Value = 250
    self.lock = Lock()
    self.lock.acquire()
    self.PRG = Random()
    Thread.__init__(self)
  #end __init__

  def run(self):

    def limit(x, sub, sup):
      if x < sub:
        return sub
      elif x > sup:
        return sup
      else:
        return x
      #end if
    #end limit

    while 1:
      if not self.Running:
        self.lock.acquire()
        self.Running = True
      #end if
      if not self.ctrl:
        return
      #end if
      OldTime = self.Time
      self.Time = OldTime +  self.PRG.randint(1,max_count)
      while OldTime < self.Time:
        OldTime += 1
      #end while
      sleep(sleep_time)
      self.Value = limit(self.Value + self.PRG.randint(-5,5), 0, 500)
      if self.ShowMode != 3:
        if self.ShowMode % 2 == 0:
          self.ShowValue = self.Value
        #end if
        if self.ShowMode / 2 == 0:
          self.ShowTime = self.Time
        #end if
        gdk.threads_enter()
        canvas.Adjust(self.Id, self.ShowTime, self.ShowValue)
        gdk.threads_leave()
      #end if
    #end while
  #end run

  def Start_Stop(self,ignore):
    if self.Running:
      self.Running = False
    else:
      try:
        self.lock.release()
      except thread_error:
        pass
    #end if
  #end Start_Stop

  def Modus(self,ignore):
    if self.Running:
      self.ShowMode = (self.ShowMode + 1) % 4
    else:
      if self.ShowMode == 0:
        self.Time = 0
        self.Value = 250
      else:
        self.ShowMode = 0
      #end if
      canvas.Adjust(self.Id, self.Time, self.Value)
    #end if
  #end Modus

  def Quit(self):
    self.ctrl = False
    if not self.Running:
      released = False
      while not released:
        try:
          self.lock.release()
          released = True
        except thread_error:
          pass
        #end try
      #end while
    #end if
  #end Quit
#end Counting

Worker = [ Counting(i) for i in xrange(7) ]

for W in sample(Worker,7):
  W.start()
#end for

RowHght = 25
BtnSize = (80, RowHght)

def index2rgb(ix, ColorScale = 3 * 65535 / 5):

  return (ColorScale * (ix & 4) >> 2,
          ColorScale * (ix & 2) >> 1,
          ColorScale * (ix & 1) >> 0)
#end index2rgb

class Canvas(gtk.DrawingArea):

  def __init__(self):

    def On_Expose(canvas, evt):
      gc = canvas.window.new_gc()
      lb = canvas.window.new_gc()
      cm = gc.get_colormap()

      for i in xrange(7):
        color = cm.alloc_color(*index2rgb(i))
        gc.set_foreground(color)
        canvas.window.draw_rectangle(gc, True, 75,  (2 * i + 1) * RowHght, canvas.ThrdInfo[i][1], RowHght )
        canvas.layout.set_text("%8d" % (canvas.ThrdInfo[i][0],))
        canvas.window.draw_layout(lb, 5, (2 * i + 1) * RowHght + canvas.TxtPad, canvas.layout)
      #end for
    #end On_Expose

    gtk.DrawingArea.__init__(self)
    self.add_events(gdk.BUTTON_PRESS_MASK)
    self.set_size_request(600, 15 * RowHght)
    self.layout = self.create_pango_layout("")
    desc = self.layout.get_context().get_font_description()
    desc.set_family("Monospace")
    self.TxtPad = desc.get_size() / (2 * pango.SCALE)
    self.ThrdInfo = [ [0, 250 ][:] for x in range(7) ]
    self.layout.set_font_description(desc)
    self.connect("expose_event", On_Expose)
    self.connect("button_press_event", self.On_Click)
  #end __init__

  def On_Click(self, evnt, info):
    for W in sample(Worker,7):
      W.Start_Stop(None)
    #end for
  #end On_Click

  def Adjust(self, ThrdIx, Time, Value):
    gc = self.window.new_gc()
    lb = self.window.new_gc()
    cm = gc.get_colormap()

    OldValue = self.ThrdInfo[ThrdIx][1]
    if OldValue < Value:
      color = cm.alloc_color(*index2rgb(ThrdIx))
      base = 75 + OldValue
    else:
      color = self.style.bg[0]
      base = 75 + Value
    #end if
    correction = abs(Value - OldValue)
    gc.set_foreground(color)
    self.window.draw_rectangle(gc, True, base, (2 * ThrdIx + 1) * RowHght, correction, RowHght)
    self.layout.set_text("%8d" % (Time,))
    self.window.begin_paint_rect((0, (2 * ThrdIx + 1) * RowHght, 75, RowHght))
    self.window.draw_layout(lb, 5, (2 * ThrdIx + 1) * RowHght + self.TxtPad, self.layout)
    self.window.end_paint()
    gdk.flush()
    self.ThrdInfo[ThrdIx] = [Time, Value]
  #end Adjust
#end Canvas

class Frame(gtk.Window):

  def __init__(self,canvas):
    gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)
    self.set_title("Thread %s Demonstration" % demo_id)

    self.connect("delete_event", self.On_Delete)

    table = gtk.Table(15, 10, True)
    self.add(table)
    self.SS_But = 7 * [None]
    self.Md_But = 7 * [None]

    for i in xrange(7):

      Btn = gtk.Button("Start/Stop")
      apply(Btn.set_size_request, BtnSize)
      Btn.connect("clicked", Worker[i].Start_Stop)
      table.attach(Btn, 0, 1, 2 * i + 1, 2 * (i + 1), 0, 0)
      Btn.show()
      self.SS_But[i] = Btn

      Btn = gtk.Button("Modus")
      apply(Btn.set_size_request, BtnSize)
      Btn.connect("clicked", Worker[i].Modus)
      table.attach(Btn, 1, 2, 2 * i + 1, 2 * (i + 1), 0, 0)
      Btn.show()
      self.Md_But[i] = Btn
    #end for

    table.attach(canvas, 2, 10, 0, 15)
    canvas.show()

    table.show()
    self.show()
  #end __init__

  def On_Delete(self, widget, evt, data=None):
    gdk.threads_leave()
    for W in sample(Worker,7):
      W.Quit()
    #end for
    for W in sample(Worker,7):
      W.join()
    #end for
    gdk.threads_enter()
    gtk.main_quit()
    return False
  #end On_Delete
#end Frame

gdk.threads_init()
canvas=Canvas()
Win=Frame(canvas)

def main():
  gtk.main()

if __name__ == "__main__":
  main()

#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import gtk
import threading, time

import gobject
gobject.threads_init()


class Buttons:

    # a thread that watches all threads
    def _watchdog(self, w, _thread):
        #print 'watching...'
        if _thread.is_alive():
            #print 'I am monitoring ..'
            return True

        print 'exiting'
        return False

    # an independed thread
    def go_thread(self, _in,_num):
#        for x in range(5):
#            print 'receving:', _in, _num

#            #self.label.set_text(str(_in))

#            rd = self.label.get_text() # thread can access stuff
#            self.label.set_text(str(float(rd)*2)) # thread can write stuff
#            time.sleep(0.5)

        #from subprocess import call
        #call('ls -R /'.split())

        import subprocess
        s = subprocess.Popen(['ls', '-R', '/'], \
        s = subprocess.Popen(['cowsay', 'hello'], \
            stderr=subprocess.STDOUT, stdout=subprocess.PIPE).communicate()[0]
        self.label.set_text(s)



    # a callback method for the button
    def button_prs(self, widget, data=None):
        print "Hello again - %s was pressed" % data

        # set label text
        self.label.set_text('34')

        # let's start a thread
        mythread = threading.Thread(target = self.go_thread,
                                    args = ('some text',25))
        mythread.start()

        # it would be good here to start a thread that monitors 
        # the health of the previous thread
        gobject.timeout_add(200, self._watchdog, self, mythread)


    def __init__(self):
        # Create a new window
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)

        self.window.set_size_request(400, 200)

        # It's a good idea to do this for all windows.
        self.window.connect("destroy", lambda wid: gtk.main_quit())
        self.window.connect("delete_event", lambda a1,a2:gtk.main_quit())

        # Create a new button and a new label
        button = gtk.Button("Execute")
        self.label = gtk.Label('just some text')
        button.set_size_request(80, 40)

        # Create vertical box for everything
        box1 = gtk.VBox(False, 0)

        # Pack the label and the button into the box
        box1.pack_start(self.label, True, True, 3)
        box1.pack_start(button, False, False, 3)

        # add box to the window
        self.window.add(box1)

        # Connect the "clicked" signal of the button to its callback
        button.connect("clicked", self.button_prs, "me")

        # show all elements
        self.window.show_all()

def main():
    Buttons()
    gtk.main()
    return 0     

if __name__ == "__main__":
    main()


import gtk,pygtk
import subprocess
import gobject
import pty, os, time

gobject.threads_init()

class CommandTextView(gtk.TextView):
    def __init__(self):
        super(CommandTextView,self).__init__()
        #self.syn_id = None
        #self.proc = None

    def run(self, w, cmd):
#        if self.proc != None and self.proc.poll() == None: # process exist and still running
#            return 0 # exiting
#            print 'process still running.'
#        if self.proc != None and self.proc.poll() != None: # process exist and not running
#            print 'killing process still running.'
#            self.stop(self)
#            while self.proc.poll() == None: # waiting to die
#                time.sleep(0.1)
        # let's start process and connect a pipe to it
        self.proc = subprocess.Popen(cmd, shell=True, bufsize=20, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print 'Begin synthesis process:', self.proc.pid
        #self.syn_id = gobject.io_add_watch(self.proc.stdout, gobject.IO_IN, self.write_to_buffer)

        # now that the synthesis process has started let's create a second process that kills it
        # and disconnects it pipe as soon as the process ends.
        #gobject.timeout_add(400, self.watchdog_fn, self)

    def stop(self,w ):
        self.proc.kill()
        print 'process terminated', self.proc.wait()
        while self.proc.poll() == None: # waiting to die
            print 'process about to die'
            time.sleep(0.1)
        #gobject.source_remove(self.syn_id) # remove synthesis pipe
        #gobject.source_remove(self.syn_id) # remove synthesis pipe
        return 0

#        if self.proc == None: # synthesis process does not exist
#            return 0
#        elif self.proc != None and self.proc.poll() == None: # synthesis process still running
#                print 'killing process and removing pipe'
#                self.proc.kill()
#                while self.proc.poll() == None: # waiting to die
#                    print 'process about to die'
#                    time.sleep(0.1)
#                gobject.source_remove(self.syn_id) # remove synthesis pipe
#                self.syn_id = None
#        elif self.proc != None: # synthesis process exist but not running
#                print 'removing pipe only and wait for process to end'
#                gobject.source_remove(self.syn_id) # remove synthesis pipe
#                self.proc.wait()
#                print 'done'
#        self.proc = None
#        self.syn_id = None


    def watchdog_fn(self,w):
        if self.proc != None and self.proc.poll() == None: # process exist and still running
            return True
        else:
            self.stop(self)
            return False # this will stop the "gobject.timeout_add"

    def write_to_buffer(self, fd, condition):
        if condition == gobject.IO_IN:
            char = fd.readline()   
            #print 1
            #buf = self.get_buffer()
            #buf.insert_at_cursor(char)
            return True
        else:
            return False

def test():
    win=gtk.Window()
    vbox = gtk.VBox(False, 0)
    win.set_size_request(300,300)
    win.connect('delete-event',lambda w,e : gtk.main_quit())
    ctv=CommandTextView()
    bt1 = gtk.Button('Run')
    bt2 = gtk.Button('Stop')
    vbox.pack_start(ctv)
    vbox.pack_end(bt2,False,False)
    vbox.pack_end(bt1,False,False)
    win.add(vbox)
    
    bt1.connect("clicked", ctv.run, 'ack-grep "test" ~/')
    bt2.connect("clicked", ctv.stop)
    win.show_all()
    gtk.main()

if __name__=='__main__': test()
    

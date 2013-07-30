import gtk,pygtk
import subprocess
import gobject
import pty, os, time
import signal, shlex

gobject.threads_init()

class CommandTextView(gtk.TextView):
    def __init__(self):
        super(CommandTextView,self).__init__()
        self.syn_id = None
        self.proc = None

    def run(self, w):

        # disable run botton
        #self.bt1.set_sensitive(False)

        # let's start process and connect a pipe to it
        cmd = "find / -name 'test'"
        spl = shlex.split(cmd)
        self.proc = subprocess.Popen(spl, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print 'Begin process:', self.proc.pid
        self.syn_id = gobject.io_add_watch(self.proc.stdout, gobject.IO_IN, self.write_to_buffer)

        # now that the synthesis process has started let's create a second process that kills it
        # and disconnects it pipe as soon as the process ends.
        gobject.timeout_add(400, self.watchdog_fn, self)

    def stop(self,w):
        self.proc.stdout.close()
        _pid = self.proc.pid
        os.kill(self.proc.pid, signal.SIGKILL)
        self.proc.wait()
        #while self.proc.poll() == None: # waiting to die
        #    time.sleep(0.1)
        gobject.source_remove(self.syn_id)
        print 'Process',_pid,'killed and its pipe closed'
        # disable stop botton

    def watchdog_fn(self,w):
        if self.proc != None and self.proc.poll() == None:
            return True # process exist and still running
        else:
            gobject.source_remove(self.syn_id)
            print 'Process naturally ended and pipe closed.'
            # enable run botton
            # disable stop botton
            return False # this will stop the "gobject.timeout_add"

    def write_to_buffer(self, fd, condition):
        if condition == gobject.IO_IN:
            char = fd.readline()   
            #print char
            buf = self.get_buffer()
            buf.insert_at_cursor(char)
            return True
        else:
            return False

def bar_timeout(pbobj):
    new_val = pbobj.pbar.get_fraction() + 0.01
    if new_val > 1.0:
        new_val = 0.0
    self.bar_timer.set_fraction(new_val)

def test():
    win=gtk.Window()
    vbox = gtk.VBox(False, 0)
    win.set_size_request(300,300)
    bar = gtk.ProgressBar()
    bar_timer = gobject.timeout_add (100, bar_timeout) # progress bar timer
    win.connect('delete-event',lambda w,e : gtk.main_quit())
    ctv=CommandTextView()
    bt1 = gtk.Button('Run')
    bt2 = gtk.Button('Stop')
    vbox.pack_start(ctv)
    vbox.pack_end(bar,False,False)
    vbox.pack_end(bt2,False,False)
    vbox.pack_end(bt1,False,False)

    win.add(vbox)
    #bt2.set_sensitive(False)
    
    bt1.connect("clicked", ctv.run)
    bt2.connect("clicked", ctv.stop)
    win.show_all()
    gtk.main()

if __name__=='__main__': test()
    

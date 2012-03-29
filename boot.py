#!/usr/bin/env python
'''
boot.py

application to compile, simulate and synthesize your vhdl code.
how to run: ./boot

Copyright (C) 2012 Fabrizio Tappero

Site:     http://www.freerangefactory.org
Author:   Fabrizio Tappero, fabrizio.tappero<at>gmail.com
License:  GNU Lesser General Public License
'''

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.


__version__ = '0.11'
__author__ = 'Fabrizio Tappero'

import pygtk, gtk, gobject, glob, os, time, sys, argparse
from gtk import gdk
pygtk.require('2.0')
from subprocess import call, Popen, PIPE, STDOUT
from multiprocessing import Process, Pipe

# some GUI images
# made with the Imagemagick command: 
#    convert stock_no_20.png -colors 14 stock_no_20.xpm
img_y_xpm=[
"20 20 12 1",
"  c #040703",
". c #365A2B",
"X c #457636",
"o c #547849",
"O c #4B8339",
"+ c #669058",
"@ c #84A779",
"# c #97B98C",
"$ c #AFC9A6",
"% c #C2D5BB",
"& c #D3E1CF",
"* c None",
"********************",
"*******     ********",
"*****  .o+X.  ******",
"**** .@##++OO  *****",
"*** o$$$#@+OOX. ****",
"** .#%&%$#++OoX  ***",
"** #$&&&$@+OOXX. ***",
"* .#%&&&$@OOOXX.  **",
"* +#%%%%#@OOOOO.. **",
"* +###$#@+OOOOXOo **",
"* +@#@@+O+OOOOO+o **",
"* X+++++OOOOOO++. **",
"** ++++OoX.oO+#+ ***",
"** .ooooXXoo+#@. ***",
"*** ..XooXo@#+. ****",
"**** ..oo++#o. *****",
"*****  .ooo.  ******",
"*******     ********",
"********************",
"********************"]

img_n_xpm=[
"20 20 12 1",
"  c #070202",
". c #5F2922",
"X c #73443E",
"o c #784C47",
"O c #8D3125",
"+ c #93443A",
"@ c #A5645C",
"# c #BF8078",
"$ c #C3847C",
"% c #D1A29C",
"& c #E7CFCC",
"* c None",
"********************",
"*******     ********",
"*****  .+@X.  ******",
"**** X@@@@++X. *****",
"*** o%%%$#@+OO. ****",
"** X%%&&$$++OOO  ***",
"** @%&&&%$+OOOO. ***",
"* .%%&&&$#OOOOOO  **",
"* +%%%&%$@OOOOOO. **",
"* @$%$%$#@OOOOOOX **",
"* +@$#@@++OOOOO@o **",
"* .@@@@+OOOOOO@#. **",
"** +@+++OOO.O@#@ ***",
"** .++++OOX@@#@. ***",
"*** ..OXOOo@#@. ****",
"**** ..Xo@@#o. *****",
"*****  .X@o.  ******",
"*******     ********",
"********************",
"********************"]


# global variables
before=[]
GUI_COMPILATION_ERROR = False
# Download and install everything that is needed for boot to function
def build():
    if 'linux' in sys.platform:             # LINUX OS
        call('clear'.split())
        print 'Downloading and install necessary packages.'
        print 'You need to be connected to the Internet.\n'
        call('sudo apt-get update'.split()) # update apt-get database
        call('sudo apt-get install python-pip python-gtk2 python-gobject'.split())
        call('sudo apt-get install ghdl gtkwave'.split())
        call('sudo pip install argparse'.split())
    elif 'darwin' in sys.platform:          # APPLE OS X
        print 'Operating system not supported.'
    elif 'win32' in sys.platform:           # WINDOWS OS
        print 'Operating system not supported.'
    elif 'cygwin' in sys.platform:          # WINDOWS OS UNDER CYGWIN
        print 'Operating system not supported.'
    else:                                   # OTHER OS
        print 'Operating system not supported.'
    print 'All done.'
    return 0

# compile vhdl project in its own process
def comp_and_sim_proc(conn):

    # some local variables (remember that we are in an indipendent process)
    COMPILATION_ERROR = False
    GTK_ALREADY_UP = False
    _border = '-'.join(['-' for num in range(25)])

    while True:
        if conn.poll():
            [wd, tl_file, comp_flag, _SOCKET_ID] = conn.recv()
        #print 'Sleeping.'
        time.sleep(0.050) # with this, this process is never busy
        try:
            if src_dir_modified(wd) and comp_flag and dir_make_sure(wd):
                # compile
                conn.send('CLEAR ALL\n')
                conn.send(_border + '  begin compiling  ' + _border + '\n')

                # clean all files
                my_cmd = 'ghdl -clean --workdir=' + wd + '/build'
                p = Popen(my_cmd, shell=True, stdout=PIPE,stderr=STDOUT)
                p.wait()

                # analyse ALL *.vhdl and *.vhd files
                all_vhdl_files = glob.glob(os.path.join(wd,'*.vhd')) + \
                                 glob.glob(os.path.join(wd,'*.vhdl'))


                for x in all_vhdl_files:
                    conn.send('Anylising: '+ x.replace(wd+'/',' ') + '\n')
                my_cmd = 'ghdl -a --workdir=' + wd + '/build ' + \
                         ' '.join(all_vhdl_files)
                p = Popen(my_cmd, shell=True, stdout=PIPE,stderr=STDOUT)
                p.wait()
                for line in p.stdout.readlines():
                    line = line.replace(wd+'/',' ')
                    conn.send(line)

                # elaborate test bench file in "build" directory
                # IMPORTANT: at this stage the top-level entity is the same
                # as the tl_file name
                tl_entity = tl_file.split('.vhd')[0]# strip extension
                print 'Compiling top-level design file:', tl_entity
                print 'This will generate a simulation file.'
                my_cmd = 'ghdl -e --workdir=' + wd + '/build ' + tl_entity
                p = Popen(my_cmd, shell=True, stdout=PIPE, stderr=STDOUT)
                p.wait()
                
                for line in p.stdout.readlines():
                    line = line.replace(wd+'/',' ')
                    conn.send(line)
                    # check for compilation errors
                    if 'compilation error' in line:
                        COMPILATION_ERROR = True
                 

                # simulate
                if not COMPILATION_ERROR:

                    # ghdl simulation options
                    GHDL_SIM_OPT ='--stop-time=100ns'

                    # move the executable tl_entity in folder "/build"
                    print 'Moving simulation file:', tl_entity
                    my_cmd = 'mv ' + tl_entity + ' ' + wd + '/build'
                    p = Popen(my_cmd, shell=True, stdout=PIPE, stderr=STDOUT)
                    p.wait()

                    # generate simulation file
                    tl_entity = tl_file.split('.vhd')[0]# strip file extension
                    print 'Simulating top-level design:', tl_entity
                    my_cmd = wd+'/build/'+tl_entity +' '+GHDL_SIM_OPT+' --vcd='+wd+'/build/'+tl_entity+'.vcd'
                    p = Popen(my_cmd, shell=True, stdout=PIPE, stderr=STDOUT)
                    p.wait()
                    for line in p.stdout.readlines():
                        line = line.replace(wd+'/',' ')
                        conn.send(line)

                    if GTK_ALREADY_UP:
                        # reload simulation file in the gtkwave GUI
                        print 'Reloading GTKWAVE'
                        cmd = 'gtkwave::reLoadFile\n'
                        p1.stdin.write(cmd)
                        p1.stdin.flush()
                        time.sleep(1.1)
                    else:
                        # start rtkwave GUI inside a terminal process
                        cmd = 'gtkwave --xid='+_SOCKET_ID+' -W'
                        p1 = Popen(cmd.split(), stdout=PIPE, stdin=PIPE, stderr=PIPE)
                        while not "Interpreter id is gtkwave" in p1.stdout.readline():
                            time.sleep(0.1)
                        print "gtkwave is up."
                        GTK_ALREADY_UP = True
                        time.sleep(0.1)

                        # load simulation file in the gtkwave GUI
                        print 'Loading GTKWAVE with file:', tl_entity+'.vcd'
                        cmd = 'gtkwave::loadFile "'+wd+'/build/'+tl_entity+'.vcd"\n'
                        p1.stdin.write(cmd)
                        p1.stdin.flush()
                        time.sleep(1)

                else:
                    print 'No simulation performed'          
                # done
                conn.send(_border + '  end compiling      ' + _border + '\n')
        except:
            pass
    return 0



# check whether any file in "wd" has been modified
def src_dir_modified(wd):
    now = []
    global before
    all_vhdl_files = glob.glob(os.path.join(wd,'*.vhd')) + \
                     glob.glob(os.path.join(wd,'*.vhdl'))

    for infile in all_vhdl_files:
        now.append([infile, os.stat(infile).st_mtime])
    if now == before: # compare files and their time stamps
        #print 'Source code has not been modified.'
        return False
    else:
        before = now
        print 'Source code has been modified.'
        return True

# check that all directories and files are good
def dir_make_sure(wd):
    # check that all dirs and files exist
    if os.path.isdir(wd):
        print "Directory structure seems good."
        # make "build" directory inside "src"
        if os.path.isdir(wd+'/build')==False:
            try:
                os.path.os.mkdir(wd+'/build')
                print '"build" directory created.'
            except:
                print 'Hum... you might not have writing permissions \
                       for the folder "src". Exiting.'
                return False
        else:
            for root, dirs, fls in os.walk(wd+'/build'):
                    for fl in fls:
                        os.remove(wd+'/build/'+fl) # delete "build" content
        # analyzing all *.vhdl and *.vhd files
        all_vhdl_files = glob.glob(os.path.join(wd,'*.vhd')) + \
                         glob.glob(os.path.join(wd,'*.vhdl'))

        if len(all_vhdl_files)==0:
            print "You do not seem to have any vhdl file."
            return False
        else:
            return True
    else:
        print "The selected top-level design file does not exist or is not a file."
        return False

############################# GUI CLASS BEGIN ##################################
class mk_gui:

    # function to create a new file (unless it already exist)
    def make_new_file(self, widget):
        full_path_file = self.dir_entry.get_text()
        if os.path.isdir(full_path_file):
            print 'Wrong file name format. No file created.'
            return 1
        elif not os.path.isfile(full_path_file):
            # pop up a OK CANCEL confirmation window
            answer = self.on_warn("The following file will be created:  " +
                                   os.path.basename(full_path_file))
            # create file
            if answer == gtk.RESPONSE_OK:
                open(full_path_file, 'w').close()
                print 'New file created.'
            else:
                print 'File not created.'
        else:
            print 'This file already exists, no file created.'
            #self.on_warn('This file already exist. Nothing to do.')
            return 1
        return 0

    # function to deleted file when top-level design file entry
    # is in focus and ctrl+D is pressed
    def entry_keypress(self, widget, event):
        # detect ctrl+D key pressed
        if event.keyval in (gtk.keysyms.D, gtk.keysyms.d) and \
                 event.state & gtk.gdk.CONTROL_MASK:
            full_path_file = self.dir_entry.get_text()
            # if a directory is selected, do nothing
            if os.path.isdir(full_path_file):
                print 'Wrong file name format. No file deleted.'
                self.on_warn('Wrong file name format. No file deleted.')
                return 1
            # if a file is selected delete it
            elif os.path.isfile(full_path_file):
                # pop up a OK CANCEL confirmation window
                answer = self.on_warn("The following file will be deleted:  " +
                                       os.path.basename(full_path_file))
                if answer == gtk.RESPONSE_OK:
                    os.remove(full_path_file)
                    print 'File deleted.'
                else:
                    print 'File not deleted.'
            else:
                print "This file does not exist. No file deleted."
                self.on_warn('This file does not exist. No file deleted.')
                return 1
        else:
            pass
        return 0

    # function to generate a drop down menu for the top-level design file entry
    def entry_keypress_down(self, widget, event):
        # detect arrow Down key pressed
        if event.keyval == gtk.keysyms.Down:
            print 'bingo'
            full_path_file = self.dir_entry.get_text()

            
        return 0

    # function that runs when you tick the box "auto compile"
    def chk1_changed(self, widget):
        # working directory
        wd = os.path.dirname(os.path.realpath(self.dir_entry.get_text()))
        # top-level design file
        tl_file = os.path.basename(self.dir_entry.get_text())
        # check status of the check box and compile
        if self.chk1.get_active():
            # drive compilation process
            self.comp_comm_i.send([wd, tl_file, True, self.GTKWAVE_COMM_SOCKET_ID]) # START
            print 'active'
        else:
            self.comp_comm_i.send([wd, tl_file, False, self.GTKWAVE_COMM_SOCKET_ID]) # STOP
            print 'inactive'
        return 0

    # function that runs when you press the select file button
    def select_file(self, widget):
        dialog = gtk.FileChooserDialog(
                 "Choose top-level VHDL design file", None,
                 gtk.FILE_CHOOSER_ACTION_OPEN,
                 (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                 gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        dialog.set_default_response(gtk.RESPONSE_OK)
        _dir=os.path.dirname(os.path.realpath(self.dir_entry.get_text()))
        dialog.set_current_folder(_dir)
        print _dir
        filter = gtk.FileFilter()
        filter.set_name(".vhdl files")
        filter.add_pattern("*.vhdl")
        filter.add_pattern("*.vhd")
        dialog.add_filter(filter)

        filter = gtk.FileFilter()
        filter.set_name("All files")
        filter.add_pattern("*")
        dialog.add_filter(filter)
        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            print dialog.get_filename(), 'selected'
            self.dir_entry.set_text(dialog.get_filename())
        elif response == gtk.RESPONSE_CANCEL:
            pass
        dialog.destroy()
        return 0

    # function that runs when top-level design file entry is modified
    def dir_entry_changed(self, widget):
        if os.path.isfile(self.dir_entry.get_text()) and \
           ('.vhd' in os.path.basename(self.dir_entry.get_text())):
            # valid top-level vhdl file name
            compile_output = 'Valid top-level file.\n'
            self.chk1.set_sensitive(True)

            # working directory
            wd = os.path.dirname(os.path.realpath(self.dir_entry.get_text()))
            # top-level design file
            tl_file = os.path.basename(self.dir_entry.get_text())

            # check status of check box, "src" directory and possibly compile
            if self.chk1.get_active():
                # COMPILE
                # drive compilation process
                # TODO: we are here, it seems that comp_comm_i is not visible
                #self.comp_comm_i.send([wd, tl_file, True, self.GTKWAVE_COMM_SOCKET_ID]) # START
                print '# active'
            else:
                #self.comp_comm_i.send([wd, tl_file, False, self.GTKWAVE_COMM_SOCKET_ID]) # STOP
                print '# inactive'
        else:
            compile_output = 'Please select your vhdl top level design file.'
            self.chk1.set_sensitive(False)
            self.img_y.set_sensitive(False)
            self.img_n.set_sensitive(False)

        self.txt.set_markup('<span size="11000" foreground="black">'+
                             compile_output +'</span>') 
        return 0

    # delete and kill main window
    def delete(self, widget, event=None):
        gtk.main_quit()
        return False

    # method to attach pipes to the GUI
    def add_conn(self, comp_comm_i, sim_comm_i):
        # pipes for compilation and simulation processes
        self.comp_comm_i = comp_comm_i
        self.sim_comm_i = sim_comm_i
        # attach the pipe output to the method "update_gui"
        # inspired by: http://haltcondition.net/?p=2319
        fd = comp_comm_i.fileno()
        gobject.io_add_watch(fd, gobject.IO_IN, self.update_gui)
        return 0

    # method to update GUI with pipe information
    def update_gui(self, fd, cond):
        global GUI_COMPILATION_ERROR
        
        # update compiling tab
        val=self.comp_comm_i.recv()
        self.txt.set_markup(self.txt.get_text() +
                       '<span size="11000" foreground="black">'+ val +'</span>')
        if 'begin compiling'in val:
            self.img_y.set_sensitive(False) # green light off
            self.img_n.set_sensitive(True)  # red light one
            GUI_COMPILATION_ERROR = False
        elif 'compilation error' in val:
            self.img_y.set_sensitive(False) # green light off
            self.img_n.set_sensitive(True)  # red light one
            GUI_COMPILATION_ERROR = True
            print 'Compilation error.'
        elif  'end compiling'in val and (not GUI_COMPILATION_ERROR):
            self.img_y.set_sensitive(True)  # green light on
            self.img_n.set_sensitive(False) # red light off
            print 'Compiled successfully.'
        elif 'CLEAR ALL' in val:
            # clean compiling tab area
            self.txt.set_markup('<span size="11000" foreground="black"></span>')
        return True

    # general purpose OK CANCEL message dialog
    def on_warn(self, _text=''):
        md = gtk.MessageDialog(self.window, 
            gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_INFO, 
            gtk.BUTTONS_OK_CANCEL, _text)
        answer = md.run()
        md.destroy()
        return answer

    def __init__(self):

        # make the main window
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.connect("delete_event", self.delete)
        self.window.set_border_width(2)
        self.window.set_size_request(840, 500)
        self.window.set_title("freerangefactory.org - BOOT ver. " + __version__)
        
        # make a 1X1 table to put the tabs in (this table is not really needed)
        table = gtk.Table(rows=1, columns=1, homogeneous=False)
        self.window.add(table)

        # Create a notebook and place it inside the table
        notebook = gtk.Notebook()
        notebook.set_tab_pos(gtk.POS_TOP)
        table.attach(child=notebook, left_attach=0, right_attach=1, 
                     top_attach=0, bottom_attach=1, xpadding=0, ypadding=0)

        # LOAD CONTENT into Compile tab
        Vbox1 = gtk.VBox(False, 0)
        notebook.append_page(Vbox1, gtk.Label('Compile')) # load

        # make socket for boot => gtkwave communication
        self.socket = gtk.Socket()

        # make Simulate tab and connect to socket
        Vbox2 = gtk.VBox(False, 0)
        Vbox2.pack_start(self.socket, True, True,0) #put socket inside vbox
        notebook.append_page(Vbox2, gtk.Label('Simulate')) # load vbox into tab

        # start socket
        #Vbox1.pack_start(self.socket, True, True,0) #put socket inside vbox
        self.GTKWAVE_COMM_SOCKET_ID = hex(self.socket.get_id())[:-1]
        # you now need to start GTKWAVE with this ID in this way:
        # gtkwave --xid=0x320003e -W
        # where 0x320003e=self.GTKWAVE_COMM_SOCKET_ID
        print 'GtkWave Comm. socket ID:', self.GTKWAVE_COMM_SOCKET_ID
        self.socket.add_id(long(360002))

        # make check box "auto compile"
        self.chk1 = gtk.CheckButton("auto compile")
        self.chk1.set_active(False)
        self.chk1.set_sensitive(False)
        # let's trigger an action when the check box changes
        self.chk1.connect("clicked", self.chk1_changed)

        # make compile error notification area
        self.notif_layout = gtk.Layout(None, None)
        self.notif_layout.set_size(650, 900)
        # generate vertical scrollbar
        vScrollbar = gtk.VScrollbar(None)
        table = gtk.Table(1, 2, False)
        table.attach(vScrollbar, 1, 2, 0, 1, gtk.FILL|gtk.SHRINK,
                     gtk.FILL|gtk.SHRINK, 0, 2)
        table.attach(self.notif_layout, 0, 1, 0, 1, gtk.FILL|gtk.EXPAND,
	                 gtk.FILL|gtk.EXPAND, 0, 2)

        vAdjust = self.notif_layout.get_vadjustment()
        vScrollbar.set_adjustment(vAdjust)

        self.txt = gtk.Label()
        self.txt.set_use_markup(gtk.TRUE)
        compile_output = 'Please select your vhdl top level design file.'
        self.txt.set_markup('<span size="11000" foreground="black">'+ \
                             compile_output +'</span>')
        self.notif_layout.add(self.txt)
            
        # make directory entry
        self.dir_entry = gtk.Entry()

        # let's trigger an action when the text changes
        self.dir_entry.connect("changed", self.dir_entry_changed)

        # let's trigger a "creare file" action when the return key is pressed
        self.dir_entry.connect("activate", self.make_new_file)

        # let's trigger a "delete file" action when top-level design file entry
        # is in focus and ctrl+D is pressed
        self.dir_entry.connect('key-press-event', self.entry_keypress)

        # let's trigger a drop down menu action when the top-level design
        # file entry can show files and folders and down arrow is pressed
        self.dir_entry.connect('key-press-event', self.entry_keypress_down)

        # make icons
        self.window.show() # unfortunately this is needed
        self.img_n = gtk.Image()
        pixmap,mask = gdk.pixmap_create_from_xpm_d(self.window.window,None,img_n_xpm)
        self.img_n.set_from_pixmap(pixmap, mask)

        self.img_y = gtk.Image()
        pixmap,mask = gdk.pixmap_create_from_xpm_d(self.window.window,None,img_y_xpm)
        self.img_y.set_from_pixmap(pixmap, mask)

        self.img_ind = gtk.Image()
        self.img_ind.set_from_stock(gtk.STOCK_INDEX, gtk.ICON_SIZE_BUTTON)
        self.img_y.set_sensitive(False)
        self.img_n.set_sensitive(False)

        # make icon-button
        btn_ind = gtk.Button()
        btn_ind.add(self.img_ind)
        btn_ind.connect("clicked", self.select_file)

        # put stuff together in the window
        Hbox1 = gtk.HBox(False, 0)
        Hbox1.pack_start(btn_ind, False, False, 0)
        Hbox1.pack_start(self.dir_entry, True, True, 0)
        Hbox1.pack_end(self.img_n, False, False, 2)
        Hbox1.pack_end(self.img_y, False, False, 2)
        Hbox1.pack_end(self.chk1, False, False, 0)
        Vbox1.pack_start(Hbox1, False, False, 0)

        # make a small label
        lb1 = gtk.Label()
        fixed = gtk.Fixed()
        lb1.set_use_markup(gtk.TRUE)
        lb1.set_markup('<span size="8000" \
                        foreground="#B5B2AC">top-level VHDL design file</span>')
        fixed.put(lb1,35,0)
        Vbox1.pack_start(fixed, False, False, 0)

        # make line separator
        separator = gtk.HSeparator()
        Vbox1.pack_start(separator, False, False, 10)

        # add compile notification area to window
        Vbox1.pack_start(table, True, True	, 0)

        # set current working dir as starting point and get all vhdl files in it
        wd = os.getcwd()
        vhdl_files = glob.glob(os.path.join(wd,'*.vhd')) + \
                     glob.glob(os.path.join(wd,'*.vhdl'))

        # attempt to set and load "src" directory inside the current working dir
        new_wd = os.path.join(os.getcwd(),'src')
        if os.path.isdir(new_wd):
            wd = new_wd
            vhdl_files = []
            new_vhdl_files = glob.glob(os.path.join(wd,'*.vhd')) + \
                             glob.glob(os.path.join(wd,'*.vhdl'))

            if len(new_vhdl_files) !=0:
                vhdl_files = new_vhdl_files

        print 'Your current working directory is:', wd
        self.dir_entry.set_text(wd)
        
        # load vhdl file by picking the last .vhd* file 
        if len(vhdl_files)!=0:
            best_guess_vhdl_file = os.path.join(wd,vhdl_files[-1])
            self.dir_entry.set_text(best_guess_vhdl_file)
            # possibly load the first "*_td.vhd*" file
            possible_vhdl_td = glob.glob(os.path.join(wd,'*_td.vhd')) + \
                               glob.glob(os.path.join(wd,'*_td.vhdl'))

            if len(possible_vhdl_td)!=0:
                self.dir_entry.set_text(os.path.join(wd,possible_vhdl_td[0]))

        # load help content into Help tab
        import urllib
        try:
            f = urllib.urlopen( \
                "http://www.freerangefactory.org/dl/boot/boot_help.txt")
            help_content = f.read()
            f.close()
        except:
            help_content = '<span foreground="#B5B2AC">\nThis is a dynamic \
                            help page taken from the Internet.\n'
            help_content += 'Currently, you do no seem to be on-line.</span>'

        # make help area
        help_layout = gtk.Layout(None, None)
        help_layout.set_size(650, 900)

        # generate vertical scrollbar
        vScrollbar = gtk.VScrollbar(None)
        table1 = gtk.Table(1, 2, False)
        table1.attach(vScrollbar, 1, 2, 0, 1, gtk.FILL|gtk.SHRINK,
                     gtk.FILL|gtk.SHRINK, 0, 2)
        table1.attach(help_layout, 0, 1, 0, 1, gtk.FILL|gtk.EXPAND,
	                 gtk.FILL|gtk.EXPAND, 0, 2)

        vAdjust = help_layout.get_vadjustment()
        vScrollbar.set_adjustment(vAdjust)

        lb0 = gtk.Label()
        lb0.set_use_markup(gtk.TRUE)
        lb0.set_markup('<span size="11000" foreground="black">' \
                        + help_content +'</span>') # load content in tab area
        lb0.set_alignment(0, 0)
        notebook.append_page(table1, gtk.Label('Help')) # load
        help_layout.add(lb0)
        
        # show all the widgets
        self.window.show_all()
############################# GUI CLASS END ####################################

# turn on the GUI
def gui_up():
    gtk.main()
    return 0

# MAIN
def main():

    # create and start process for compile task
    comp_comm_i, comp_comm_o = Pipe()
    comp_prc = Process(target=comp_and_sim_proc, args=(comp_comm_o,))
    comp_prc.start()

    # create and start process for simulation task
    sim_comm_i, sim_comm_o = Pipe()
    #sim_prc = Process(target=sim_prj_prc, args=(sim_comm_o,))
    #sim_prc.start()

    # make gui object and start it.
    # the two communication pipes are passed to the GUI
    my_gui = mk_gui()
    my_gui.add_conn(comp_comm_i, sim_comm_i)
    gui_up()

    # terminate all processes
    comp_prc.terminate()
    #sim_prc.terminate()
    comp_prc.join()
    #sim_prc.join()
    return 0

# to be executed when you call "./boot.py"
if __name__ == "__main__":
    # load parser for help options
    parser = argparse.ArgumentParser(
             description='Program to compile and simulate your VHDL code.',
             epilog="Program is made by: freerangefactory.org")

    parser.add_argument('-b','--build', required=False, dest='build', 
                        action='store_const', const=True, default=False,
                        help='Download and install necessary packages \
                              (Internet connection required)')

    args = parser.parse_args()

    # load stuff accordingly
    try:
        if args.build:
            build()
        else:
            # redirect standard output
            #sys.stdout = open('boot.log', 'w')
            #sys.stdout = open('/dev/null', 'w')
            main()
    except KeyboardInterrupt:
        print 'bye bye.'




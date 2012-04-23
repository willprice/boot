#!/usr/bin/env python
'''
FILE: boot

application to compile, simulate and synthesize your VHDL code.
how to run: ./boot

Copyright (C) 2012 Fabrizio Tappero

Site:     http://www.freerangefactory.org
Author:   Fabrizio Tappero, fabrizio.tappero<at>gmail.com
License:  GNU Lesser General Public License
'''

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as 
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

__version__ = 0.14
__author__ = 'Fabrizio Tappero'

import pygtk, gtk, gobject, glob, os, time, sys, argparse
import ConfigParser, webkit, httplib
from gtk import gdk
pygtk.require('2.0')
from subprocess import call, Popen, PIPE, STDOUT
from multiprocessing import Process, Pipe

# Xilinx device data
# # http://www.xilinx.com/support/index.htm
dev_manufacturer  = ['Xilinx', 'Altera', 'Actel'] 
dev_family  = ['Spartan-6' ,'Spartan-3','Spartan-3A_DSP', 'Artix', 'Kintex', 'Virtex', 'Zynq', 'CoolRunner', 'XC9500X'] 
dev_device=['Zynq-7000 XC7Z010','Zynq-7000 XC7Z020','Zynq-7000 XC7Z030','Zynq-7000 XC7Z045','Artix-7 XC7A100T','Artix-7 XC7A200T',
'Artix-7 XC7A350T','Kintex-7 XC7K70T','Kintex-7 XC7K160T','Kintex-7 XC7K325T','Kintex-7 XC7K355T','Kintex-7 XC7K410T','Kintex-7 XC7K420T',
'Kintex-7 XC7K480T','Virtex-7 XC7V585T','Virtex-7 XC7V1500T','Virtex-7 XC7V2000T','Virtex-7 XC7VX330T','Virtex-7 XC7VX415T',
'Virtex-7 XC7VX485T','Virtex-7 XC7VX550T','Virtex-7 XC7VX690T','Virtex-7 XC7VX980T','Virtex-7 XC7VX1140T','Virtex-7 XC7VH290T',
'Virtex-7 XC7VH580T','Virtex-7 XC7VH870T','Virtex-6 XC6VLX75T','Virtex-6 XC6VLX130T','Virtex-6 XC6VLX195T','Virtex-6 XC6VLX240T ',
'Virtex-6 XC6VLX365T','Virtex-6 XC6VLX550T','Virtex-6 XC6VLX760','Virtex-6 XC6VSX315T','Virtex-6 XC6VSX475T','Virtex-6 XC6VHX250T',
'Virtex-6 XC6VHX255T','Virtex-6 XC6VHX380T','Virtex-6 XC6VHX565T','Virtex-6Q XQ6VLX130T','Virtex-6Q XQ6VLX240T','Virtex-6Q XQ6VLX550T',
'Virtex-6Q XQ6VSX315T','Virtex-6Q XQ6VSX475T','Virtex-5 XC5VLX30','Virtex-5 XC5VLX50','Virtex-5 XC5VLX85','Virtex-5 XC5VLX110',
'Virtex-5 XC5VLX155','Virtex-5 XC5VLX220','Virtex-5 XC5VLX330','Virtex-5 XC5VLX20T','Virtex-5 XC5VLX30T','Virtex-5 XC5VLX50T',
'Virtex-5 XC5VLX85T','Virtex-5 XC5VLX110T','Virtex-5 XC5VLX155T','Virtex-5 XC5VLX220T','Virtex-5 XC5VLX330T','Virtex-5 XC5VSX35T',
'Virtex-5 XC5VSX50T','Virtex-5 XC5VSX95T','Virtex-5 XC5VSX240T','Virtex-5 XC5VFX30T','Virtex-5 XC5VFX70T','Virtex-5 XC5VFX100T',
'Virtex-5 XC5VFX130T','Virtex-5 XC5VFX200T','Virtex-5Q XQ5VLX85','Virtex-5Q XQ5VLX110','Virtex-5Q XQ5VLX30T','Virtex-5Q XQ5VLX110T',
'Virtex-5Q XQ5VLX155T','Virtex-5Q XQ5VLX220T','Virtex-5Q XQ5VLX330T','Virtex-5Q XQ5VSX50T','Virtex-5Q XQ5VSX95T','Virtex-5Q XQ5VSX240T',
'Virtex-5Q XQ5VFX70T','Virtex-5Q XQ5VFX100T','Virtex-5Q XQ5VFX130T','Virtex-5Q XQ5VFX200T','Virtex-5QV XQR5VFX130','Virtex-4 XC4VLX15',
'Virtex-4 XC4VLX25','Virtex-4 XC4VLX40','Virtex-4 XC4VLX60','Virtex-4 XC4VLX80','Virtex-4 XC4VLX100','Virtex-4 XC4VLX160',
'Virtex-4 XC4VLX200','Virtex-4 XC4VSX25','Virtex-4 XC4VSX35','Virtex-4 XC4VSX55','Virtex-4 XC4VFX12','Virtex-4 XC4VFX20',
'Virtex-4 XC4VFX40','Virtex-4 XC4VFX60','Virtex-4 XC4VFX100','Virtex-4 XC4VFX140','Virtex-4Q XQ4VLX25','Virtex-4Q XQ4VLX40',
'Virtex-4Q XQ4VLX60','Virtex-4Q XQ4VLX80','Virtex-4Q XQ4VLX100','Virtex-4Q XQ4VLX160','Virtex-4Q XQ4VSX55','Virtex-4Q XQ4VFX60',
'Virtex-4Q XQ4VFX100','Virtex-4QV XQR4VSX55','Virtex-4QV XQR4VFX60','Virtex-4QV XQR4VFX140','Virtex-4QV XQR4VLX200','Spartan-6 XC6SLX4',
'Spartan-6 XC6SLX9','Spartan-6 XC6SLX16','Spartan-6 XC6SLX25','Spartan-6 XC6SLX45','Spartan-6 XC6SLX75','Spartan-6 XC6SLX100',
'Spartan-6 XC6SLX150','Spartan-6 XC6SLX25T','Spartan-6 XC6SLX45T','Spartan-6 XC6SLX75T','Spartan-6 XC6SLX100T','Spartan-6 XC6SLX150T',
'Spartan-6Q XQ6SLX75','Spartan-6Q XQ6SLX150','Spartan-6Q XQ6SLX75T','Spartan-6Q XQ6SLX150T','Spartan-3A_DSP XC3SD1800A',
'Spartan-3A_DSP XC3SD3400A','Spartan-3AN XC3S50AN','Spartan-3AN XC3S200AN','Spartan-3AN XC3S400AN','Spartan-3AN XC3S700AN',
'Spartan-3AN XC3S1400AN','Spartan-3A XC3S50A','Spartan-3A XC3S200A','Spartan-3A XC3S400A','Spartan-3A XC3S700A','Spartan-3A XC3S1400A',
'Spartan-3L XC3S1000L','Spartan-3L XC3S1500L','Spartan-3L XC3S4000L','Spartan-3E XC3S100E','Spartan-3E XC3S250E','Spartan-3E XC3S500E',
'Spartan-3E XC3S1200E','Spartan-3E XC3S1600E','Spartan-3 XC3S50','Spartan-3 XC3S200','Spartan-3 XC3S400','Spartan-3 XC3S1000',
'Spartan-3 XC3S1500','Spartan-3 XC3S2000','Spartan-3 XC3S4000','Spartan-3 XC3S5000','CoolRunner-II XC2C32A','CoolRunner-II XC2C64A',
'CoolRunner-II XC2C128','CoolRunner-II XC2C256','CoolRunner-II XC2C384','CoolRunner-II XC2C512','XC9500XL XC9536XL','XC9500XL XC9572XL',
'XC9500XL XC95144XL','XC9500XL XC95288XL']

#dev_device = [x.split()[1] for x in dev_device]
dev_package = ['VQ(G)100','TQ(G)100','CP(G)132','TQ(G)144','CS(G)144','PQ(G)208']
dev_speed = ['-L1','-1','-2','-3','-3N','-4','-5','-6','-7','-10','-11','-12']

# some GUI images made with the Imagemagick command: 
#    convert stock_no_20.png -colors 14 stock_no_20.xpm
img_y_xpm=[
"20 20 12 1","  c #040703",". c #365A2B","X c #457636","o c #547849",
"O c #4B8339","+ c #669058","@ c #84A779","# c #97B98C","$ c #AFC9A6",
"% c #C2D5BB","& c #D3E1CF","* c None",
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
"20 20 12 1","  c #070202",". c #5F2922","X c #73443E","o c #784C47",
"O c #8D3125","+ c #93443A","@ c #A5645C","# c #BF8078","$ c #C3847C",
"% c #D1A29C","& c #E7CFCC","* c None",
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
    if 'linux' in sys.platform:                                       # LINUX OS
        call('clear'.split())
        print 'Downloading and install necessary packages.'
        print 'You need to be connected to the Internet.\n'
        call('sudo apt-get update'.split()) # update apt-get database
        call('sudo apt-get install python-pip'.split())
        call('sudo apt-get install python-gtk2 python-gobject'.split())
        call('sudo apt-get install gtk2-engines-pixbuf'.split())
        call('sudo apt-get install ghdl gtkwave'.split())
        call('sudo pip install argparse'.split())
    elif 'darwin' in sys.platform:                                  # APPLE OS X
        print 'Operating system not supported.'
        pass
    elif 'win32' in sys.platform:                                   # WINDOWS OS
        print 'Operating system not supported.'
        pass
    elif 'cygwin' in sys.platform:                     # WINDOWS OS UNDER CYGWIN
        print 'Operating system not supported.'
        pass
    else:                                                             # OTHER OS
        print 'Operating system not supported.'
        pass
    print 'All done.'
    return 0

# compile and simulate VHDL project in ITS OWN PROCESS (notice that this is not
# done in a thread but instead in a completely indipended process)
# this process/function is written in this way because we want it to be ready
# to run whenever the user saves/modifies any of the VHDL source files.
# in future rework, the use of gobject.timeout_add() is maybe advisable. More info:
# /usr/share/doc/python-gtk2-tutorial/html/ch-TimeoutsIOAndIdleFunctions.html
def comp_and_sim_proc(conn):

    # some local variables (remember that we are in an independent process)
    COMPILATION_ERROR = False
    GTK_ALREADY_UP = False
    _border = '-'.join(['-' for num in range(35)])

    # let's keep this process running in the background
    while True:
        if conn.poll():
            [wd, tl_file, comp_flag, comp_rerun, _SOCKET_ID, GHDL_SIM_OPT] \
            = conn.recv()
        #print 'Sleeping.'
        time.sleep(0.50) # with this, this process is never busy
        try:
            if src_dir_modified(wd) and comp_flag and dir_make_sure(wd) or \
               (comp_rerun and comp_flag):

                # compile

                # clean up GUI
                conn.send('CLEAR ALL\n')
                conn.send(_border + '  begin compiling  ' + _border + '\n')

                # clean all GHDL files
                my_cmd = 'ghdl -clean --workdir=' + wd + '/build'
                p = Popen(my_cmd, shell=True, stdout=PIPE, stderr=STDOUT)
                p.wait()

                # analyze ALL *.vhdl and *.vhd files
                all_vhdl_files = glob.glob(os.path.join(wd,'*.vhd')) + \
                                 glob.glob(os.path.join(wd,'*.vhdl'))
                print 'Checking all VHDL files in:', wd
                for x in all_vhdl_files:
                    conn.send('Checking: '+ x.replace(wd+'/',' ') + '\n')
                my_cmd = 'ghdl -a --workdir=' + wd + '/build ' + \
                         ' '.join(all_vhdl_files)
                p = Popen(my_cmd, shell=True, stdout=PIPE, stderr=STDOUT)
                p.wait()
                for line in p.stdout.readlines():
                    line = line.replace(wd+'/',' ')
                    conn.send(line)

                # elaborate test bench file inside "build" directory
                # IMPORTANT: at this stage the top-level entity is the same
                # as the tl_file name
                tl_entity = tl_file.split('.vhd')[0]# strip extension
                print 'Compiling top-level design file:', tl_entity
                my_cmd = 'ghdl -e --workdir=' + wd + '/build ' + tl_entity
                p = Popen(my_cmd, shell=True, stdout=PIPE, stderr=STDOUT)
                p.wait()
                
                for line in p.stdout.readlines():
                    line = line.replace(wd+'/',' ')
                    conn.send(line)
                    # check for compilation errors
                    if 'compilation error' in line:
                        COMPILATION_ERROR = True 
                        print 'Compilation error occurred.'              

                # simulate
                if not COMPILATION_ERROR:
                    
                    # notify the beginning of a simulation
                    conn.send(_border + '  begin simulation ' + _border + '\n')

                    # move the executable tl_entity in folder "/build"
                    print 'Moving simulation file:', tl_entity
                    my_cmd = 'mv ' + tl_entity + ' ' + wd + '/build'
                    p = Popen(my_cmd, shell=True, stdout=PIPE, stderr=STDOUT)
                    p.wait()

                    # generate simulation file
                    tl_entity = tl_file.split('.vhd')[0]# strip file extension
                    print 'Simulating top-level design:', tl_entity
                    my_cmd = wd + '/build/' + tl_entity + ' ' + GHDL_SIM_OPT \
                             + ' --vcd='+wd+'/build/simul_output.vcd'
                    p = Popen(my_cmd, shell=True, stdout=PIPE, stderr=STDOUT)
                    p.wait()
                    for line in p.stdout.readlines():
                        line = line.replace(wd+'/',' ')
                        conn.send(line)

                    # load the simulation output file with 
                    if GTK_ALREADY_UP:
                        # reload simulation file in the gtkwave GUI
                        print 'Reloading GTKWAVE simulation file.'
                        cmd = 'gtkwave::reLoadFile\n'
                        p1.stdin.write(cmd)
                        p1.stdin.flush()
                        #time.sleep(1.1)
                    else:
                        # start rtkwave GUI inside a terminal process
                        cmd = 'gtkwave' + \
                              ' --rcfile='+ wd + '/build/gtkwaverc' + \
                              ' --xid=' + _SOCKET_ID + \
                              ' -W'
                        p1 = Popen(cmd.split(), stdout=PIPE, stdin=PIPE, stderr=PIPE)
                        while not "Interpreter id is gtkwave" in p1.stdout.readline():
                            time.sleep(0.1)
                        print "gtkwave is up."
                        GTK_ALREADY_UP = True
                        time.sleep(0.3)

                        # load simulation file in the gtkwave GUI
                        print 'Loading simulation interface with file:', tl_entity+'.vcd'
                        cmd = 'gtkwave::loadFile "'+wd+'/build/simul_output.vcd"\n'
                        p1.stdin.write(cmd)
                        p1.stdin.flush()
                        time.sleep(0.3)
                else:
                    print 'No simulation performed.'    
      
                # done
                COMPILATION_ERROR = False
                conn.send(_border + '   end processing   ' + _border + '\n')                                              
        except:
            pass
    return 0

# check whether any VHDL file in folder "wd" has been modified
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

# check that all directories and files inside wd are good
# if the "build" directory exists, delete its content
# if "build" directory does not exist, create it
def dir_make_sure(wd):
    # check that all directories and files exist
    if os.path.isdir(wd):
        print "Directory structure seems good."
        # make "build" directory inside wd
        if os.path.isdir(os.path.join(wd,'build'))==False:
            try:
                os.path.os.mkdir(os.path.join(wd,'build'))
                os.path.os.mkdir(os.path.join(wd,'build','out'))
                print '"build" directory created.'

            except:
                print 'Hum... you might not have writing permissions \
                       for the folder you are in... Exiting.'
                return False
        else:
            # delete all files inside the "build" directory
            for root, dirs, fls in os.walk(os.path.join(wd,'build')):
                for fl in fls:
                    os.remove(os.path.join(wd,'build',fl))
            print 'All files inside "build" were deleted.'
            # delete all files inside the "build/out" directory
            for root, dirs, fls in os.walk(os.path.join(wd,'build','out')):
                for fl in fls:
                    os.remove(os.path.join(wd,'build','out',fl))
            print 'All files inside "build/out" were deleted.'

        # save gtkwave configuration file inside "build" folder
        print 'Creating gtkwave configuration file inside "build" folder'
        gtkwave_cnf_cont = '# gtkwave custom configuration file\n'+ \
                           '#\n# eliminate some keys\n#\n'+ \
                           'accel "/File/Read Sim Logfile" (null)\n'+ \
                           'accel "/Edit/Toggle Trace Hier" (null)\n'+ \
                           'accel "/Edit/Toggle Group Open|Close" (null)\n'+ \
                           'accel "/Edit/Create Group" (null)\n'+ \
                           'accel "/Markers/Locking/Lock to Lesser Named Marker" (null)\n'+ \
                           'accel "/Markers/Locking/Lock to Greater Named Marker" (null)\n'+ \
                           'accel "/Markers/Locking/Unlock from Named Marker" (null)\n'
        gtkwave_cnf_fl = os.path.join(wd,'build','gtkwaverc')
        open(gtkwave_cnf_fl, 'w').write(gtkwave_cnf_cont)

        # analyzing all *.vhdl and *.vhd files
        all_vhdl_files = glob.glob(os.path.join(wd,'*.vhd')) + \
                         glob.glob(os.path.join(wd,'*.vhdl'))

        if len(all_vhdl_files)==0:
            print "You do not seem to have any VHDL file."
            return False
        else:
            return True
    else:
        print "The selected top-level design file does not exist or is not a file."
        return False


#---------------------------- GUI CLASS BEGIN ----------------------------------
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
    # TODO this function is not yet implemented
    def entry_keypress_down(self, widget, event):
        # detect arrow Down key pressed
        if event.keyval == gtk.keysyms.Down:
            print 'bingo'
            full_path_file = self.dir_entry.get_text()           
        return 0

    # function that runs when you tick the box "auto compile"
    def run_compile_and_sim(self, widget, rerun=False):
        # working directory
        wd = os.path.dirname(os.path.realpath(self.dir_entry.get_text()))
        # top-level design file
        tld_file = os.path.basename(self.dir_entry.get_text())
        # simulation options
        sim_opt = self.sim_opt_entry.get_text()
        # check status of the check box and compile
        if self.chk1.get_active():
            # drive compilation process
            self.comp_comm_i.send([wd, tld_file, True, False, self.GTKWAVE_COMM_SOCKET_ID, sim_opt]) # START
            print 'active'
        else:
            self.comp_comm_i.send([wd, tld_file, False, False, self.GTKWAVE_COMM_SOCKET_ID, sim_opt]) # STOP
            print 'inactive'

        # re-run the whole compile and simulation process
        if rerun:
            chk_box_status = self.chk1.get_active()
            self.comp_comm_i.send([wd, tld_file, chk_box_status, True, self.GTKWAVE_COMM_SOCKET_ID, sim_opt]) # START
            time.sleep(0.02)
            self.comp_comm_i.send([wd, tld_file, chk_box_status, False, self.GTKWAVE_COMM_SOCKET_ID, sim_opt]) # STOP
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
        # updating the synthesis field
        self.top_level_label.set_text('Top-level design: ' \
                                      + self.dir_entry.get_text())

        # proceed with possible compile and simulate process
        compile_output = ''
        if os.path.isfile(self.dir_entry.get_text()) and \
           ('.vhd' in os.path.basename(self.dir_entry.get_text())):

            # valid top-level vhdl file name
            compile_output = 'Valid top-level VHDL design file.\n'
            self.chk1.set_sensitive(True)
            print 'Top-level design file has been updated.'

            # working directory
            wd = os.path.dirname(os.path.realpath(self.dir_entry.get_text()))
            # top-level design file
            tld_file = os.path.basename(self.dir_entry.get_text())
            # simulation options
            sim_opt = self.sim_opt_entry.get_text()

            # check status of check box and possibly compile
            if self.chk1.get_active():
                # COMPILE
                chk_box_status = self.chk1.get_active()
                self.comp_comm_i.send([wd, tld_file, chk_box_status, True, self.GTKWAVE_COMM_SOCKET_ID, sim_opt]) # START
                time.sleep(0.02)
                self.comp_comm_i.send([wd, tld_file, chk_box_status, False, self.GTKWAVE_COMM_SOCKET_ID, sim_opt]) # STOP
                print 'Forcing the compiling process and simulation process.'
            else:
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
    def add_conn(self, comp_comm_i):
        # pipes for compilation and simulation processes
        self.comp_comm_i = comp_comm_i
        # attach the pipe input to the method "update_gui"
        # inspired by: http://haltcondition.net/?p=2319
        fd = comp_comm_i.fileno()
        gobject.io_add_watch(fd, gobject.IO_IN, self.update_gui)
        return 0

    # method to update GUI with pipe information
    def update_gui(self, fd, cond):
        global GUI_COMPILATION_ERROR
        
        # update compiling tab
        val = self.comp_comm_i.recv()
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
        elif  'end processing'in val and (not GUI_COMPILATION_ERROR):
            self.img_y.set_sensitive(True)  # green light on
            self.img_n.set_sensitive(False) # red light off
            print 'Compiled successfully.'
        elif 'CLEAR ALL' in val:
            # clean compiling tab area
            pass
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

    # save some parameters in a local ~/.boot configuration file
    def save_configuration_locally(self):
        print 'Saving some parameters in local "~/.boot" file'
        # get device parameters
        ma = self.ma.get_model()[self.ma.get_active()][0]
        fa = self.fa.get_model()[self.fa.get_active()][0]
        de = self.de.get_model()[self.de.get_active()][0]
        pa = self.pa.get_model()[self.pa.get_active()][0]
        sp = self.sp.get_model()[self.sp.get_active()][0]

        # working directory
        wd = os.path.dirname(os.path.realpath(self.dir_entry.get_text()))
        # top-level design file
        tld_file = os.path.basename(self.dir_entry.get_text())
        # simulation options
        sim_opt = self.sim_opt_entry.get_text()

        # synthesis parameters
        syn_tool_path = self.tool_path_entry.get_text()
        syn_cmd = self.tool_command_entry.get_text()

        # save all
        config = ConfigParser.RawConfigParser()
        config.add_section('boot')
        config.set('boot', 'version', __version__)
        config.add_section('Last parameters')
        config.set('Last parameters', 'working directory', wd)
        config.set('Last parameters', 'top-level design file', tld_file)
        config.set('Last parameters', 'simulation options', sim_opt)

        config.set('Last parameters', 'synthesis tool path', syn_tool_path)
        config.set('Last parameters', 'synthesis command', syn_cmd)
    
        config.set('Last parameters', 'manufacturer', ma)
        config.set('Last parameters', 'family', fa)
        config.set('Last parameters', 'device', de)
        config.set('Last parameters', 'package', pa)
        config.set('Last parameters', 'speed grade', sp)

        # Writing our configuration file to '~/.boot'
        conf_file = os.path.join(os.environ['HOME'],'.boot')
        with open(conf_file, 'wb') as configfile:
            config.write(configfile)
        return 0

    # if a local ~/.boot configuration file exist, load some parameters from it
    def load_configuration_locally(self):
        conf_file = os.path.join(os.environ['HOME'],'.boot')
        if os.path.isfile(conf_file):
            print 'Loading some parameters from local "~/.boot" file' 
            #TODO: work in progress  
            # maybe we can use this makefile: http://www.xess.com/appnotes/makefile.php
        return 0

    # Start and stop the Synthesis of your vhdl design
    def syn_button_action(self, widget, action):

        # get information from Synthesis tab
        tl = self.top_level_label.get_text()
        path = self.tool_path_entry.get_text()
        cmd = self.tool_command_entry.get_text()

        # work in progress
        self.on_warn('Sorry mate, this feature is not implemented yet.')

        # execute stuff
        if action=='start':

            #save some parameters on local "~/.boot" file
            self.save_configuration_locally()
            
            # begin synthesis process unless it has been already started
            if self.syn_p!=None and self.syn_p.poll() ==None:
                print 'Synthesis process already running.'
                return 0
            print 'Starting synthesis process.'
            self.syn_p = Popen(cmd, shell=True, stdout=PIPE, stderr=STDOUT)
            # TODO work in progress

        elif action == 'stop':
            # if the synthesis process exists and is running kill it
            if type(self.syn_p) is Popen: # check data type
                try:
                    self.syn_p.kill()
                    while self.syn_p.poll() == None:
                        time.sleep(0.2)
                    print 'Synthesis process stopped.'
                except:
                    print 'Synthesis process already killed.'
        else:
            print 'Wrong synthesis command.'
        return 0

    # populate the FPGA device fields
    def make_dropdown_menu(self, data_in):
        # create a gtk.trees with data_in in it
        # note how only the last element of data_in is displayed
        store = gtk.TreeStore(str)
        for x in data_in:
            store.append(None, [x])
            #store.append(None, [x.split()[-1]])

        # create a dropdown menu with tree in it
        combo = gtk.ComboBox(store)
        combo_cell_text = gtk.CellRendererText()
        combo.pack_start(combo_cell_text, True)
        combo.add_attribute(combo_cell_text, "text", 0)
        combo.set_size_request(130, -1)
        return combo
 
    # filter device dropdown field
    def filter_dropdown(self, widget):
        # get current device family
        current_fa = self.fa.get_model()[self.fa.get_active()][0]

        # filter the content of "self.de"
        model = self.de.get_model()
        self.de.set_model(None)
        model.clear()

        # rebuild the "self.de" menu
        for x in dev_device:
            if current_fa in x:
                y=x.split()[1]
                model.append(None, [y])
        self.de.set_model(model)

        # set the first one 
        self.de.set_active(0)
        return 0

    # check for and new version of "boot" and download it
    def update_boot(self, widget):
        self.pr_pbar.set_text("checking for updates...")
    
        # Test connection health and exit if bad. If good proceed
        try:
            conn = httplib.HTTPConnection("www.freerangefactory.org")
            conn.request("GET", "/dl/boot/boot.py")
            r1 = conn.getresponse()
            #print r1.status, r1.reason # 200 OK
        except:
            print 'Internet not available'
            self.pr_pbar.set_text("you seem to be offline")
            return 1
    
        if r1.status == 200 and r1.reason == 'OK':
            new_boot_file = r1.read() # download whole boot file
    
            if '__version__' in new_boot_file:
                new_boot_ver = [x for x in new_boot_file.splitlines() if x.startswith('__version__')][0].split(' ')[-1]
                if float(new_boot_ver) > float(__version__):
                    print 'The newest boot version is:', new_boot_ver
                    print 'Your current boot version is', __version__
                    #update your current boot file
                    try:
                        fl = open(os.path.join(sys.path[0], 'boot'),'w').write(new_boot_file)
                        # TODO maybe here there is a way to allow to enter sudo password?
                        print 'File "boot" successfully updated.'
                        self.pr_pbar.set_text('file "boot" successfully updated.')
                    except:
                        print 'Problems in writing the local "boot" file.'
                        self.pr_pbar.set_text('problems in writing the local "boot" file.')
                else:
                    print 'No new available version of "boot".'
                    self.pr_pbar.set_text('no new available version of "boot".')
        else:
            print 'Problems in connecting to "freerangefactory.org"'
        return 0

    # set of methods for the help tab browser
    def go_back(self, widget, data=None):
        self.browser.go_back()
    def go_forward(self, widget, data=None):
        self.browser.go_forward()
    def go_home(self, widget, data=None):
        self.browser.open("http://www.freerangefactory.org/site/pmwiki.php/Main/BootDoc")
    def load_www(self, widge, data=None):
        url = self.www_adr_bar.get_text()
        try:
            url.index("://")
        except:
            url = "http://" + url
        self.www_adr_bar.set_text(url)
        self.browser.open(url)
    def update_buttons(self, widget, data=None):
        self.www_adr_bar.set_text( widget.get_main_frame().get_uri() )
        self.back_button.set_sensitive(self.browser.can_go_back())
        self.forward_button.set_sensitive(self.browser.can_go_forward())
    def load_progress_amount(self, webview, amount):
        self.progress.set_fraction(amount/100.0)
    def load_started(self, webview, frame):
        self.progress.set_visible(True)
    def load_finished(self, webview, frame):
        self.progress.set_visible(False)

    # constructor for the whole GUI
    def __init__(self):

        # make the main window
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.connect("delete_event", self.delete)
        self.window.set_border_width(2)
        self.window.set_size_request(890, 500)
        self.window.set_title("freerangefactory.org - BOOT ver. " + str(__version__))
        
        # make a 1X1 table to put the tabs in (this table is not really needed)
        table = gtk.Table(rows=1, columns=1, homogeneous=False)
        self.window.add(table)
        
        # make tool-tip object
        tooltips = gtk.Tooltips()

        # Create a notebook and place it inside the table
        notebook = gtk.Notebook()
        notebook.set_tab_pos(gtk.POS_TOP)
        table.attach(child=notebook, left_attach=0, right_attach=1, 
                     top_attach=0, bottom_attach=1, xpadding=0, ypadding=0)

        # LOAD CONTENT into Compile tab
        Vbox1 = gtk.VBox(False, 0)
        notebook.append_page(Vbox1, gtk.Label('Compile')) # load

        # make socket for boot => gtkwave communication
        self.my_socket = gtk.Socket()

        # make Simulate tab and connect to socket
        Vbox2 = gtk.VBox(False, 0)
        notebook.append_page(Vbox2, gtk.Label('Simulate')) # load vbox into tab

        # load some fields into Simulate tab
        Hbox3 = gtk.HBox(False, 0)
        self.sim_opt_entry = gtk.Entry()# make simulation option field entry
        self.sim_opt_entry.set_text('--stop-time=100ns')
        sim_opt_label = gtk.Label("Simulation options: ") # text label
        Hbox3.pack_start(sim_opt_label, False, False, 2)
        Hbox3.pack_start(self.sim_opt_entry, True, True, 2)
        Vbox2.pack_start(Hbox3, False, False, 0)

        # let's trigger an action when the simulation option field changes
        self.sim_opt_entry.connect("activate", self.run_compile_and_sim, True)

        # load socket into Simulate tab
        Vbox2.pack_start(self.my_socket, True, True,0) #put socket inside vbox

        # start socket
        #Vbox1.pack_start(self.my_socket, True, True,0) #put socket inside vbox
        self.GTKWAVE_COMM_SOCKET_ID = hex(self.my_socket.get_id())[:-1]
        # you now need to start GTKWAVE with this ID in this way:
        # gtkwave --xid=0x320003e -W
        # where 0x320003e=self.GTKWAVE_COMM_SOCKET_ID
        print 'GtkWave Comm. socket ID:', self.GTKWAVE_COMM_SOCKET_ID
        #self.my_socket.add_id(long(360002)) # is this necessary??

        # make check box "auto compile"
        self.chk1 = gtk.CheckButton("auto compile")
        self.chk1.set_active(False)
        self.chk1.set_sensitive(False)
        tooltips.set_tip(self.chk1, 'Automatically compile and simulate '+\
                                    'your design every time a file is modified')
        # let's trigger an action when the check box changes
        self.chk1.connect("clicked", self.run_compile_and_sim, False)

        # make compile error notification area
        self.txt = gtk.Label()
        comp_layout = gtk.Layout(None, None)
        comp_layout.set_size(650, 800)
        comp_layout.add(self.txt)

        vScrollbar = gtk.VScrollbar(None)
        comp_table = gtk.Table(1, 2, False)
        comp_table.attach(vScrollbar, 1, 2, 0, 1, gtk.FILL|gtk.SHRINK,
                     gtk.FILL|gtk.SHRINK, 0, 2)
        comp_table.attach(comp_layout, 0, 1, 0, 1, gtk.FILL|gtk.EXPAND,
	                 gtk.FILL|gtk.EXPAND, 0, 2)

        vAdjust = comp_layout.get_vadjustment()
        vScrollbar.set_adjustment(vAdjust)

        self.txt.set_use_markup(gtk.TRUE)
        compile_output = 'Select your vhdl top level design file.'
        self.txt.set_markup('<span size="11000" foreground="black">'+ \
                             compile_output +'</span>')

        # make directory entry
        self.dir_entry = gtk.Entry()
        tooltips.set_tip(self.dir_entry, "Select top-level design file")
        #self.dir_entry.set_editable(False)

        # let's trigger an action when the text changes
        self.dir_entry.connect("changed", self.dir_entry_changed)

        # let's trigger a "create file" action when the return key is pressed
        self.dir_entry.connect("activate", self.make_new_file)

        # let's trigger a "delete file" action when top-level design file entry
        # is in focus and ctrl+D is pressed
        #self.dir_entry.connect('key-press-event', self.entry_keypress)

        # let's trigger a drop down menu action when the top-level design
        # file entry can show files and folders and down arrow is pressed
        #self.dir_entry.connect('key-press-event', self.entry_keypress_down)

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
        tooltips.set_tip(btn_ind, "Select top-level design file")

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
        #separator = gtk.HSeparator()
        #Vbox1.pack_start(separator, False, False, 10)

        # add compile notification area to the compile tab
        Vbox1.pack_start(comp_table, True, True, 10)

        # make Synthesize tab 
        Hbox_syn1 = gtk.HBox(False, 0)
        Hbox_syn2 = gtk.HBox(False, 0)
        Hbox_syn3 = gtk.HBox(False, 0)
        Hbox_syn4 = gtk.HBox(False, 0)
        Hbox_syn5 = gtk.HBox(False, 0)
        Vbox_syn1 = gtk.VBox(False, 0)
        Vbox_syn1.set_border_width(10)
        self.top_level_label = gtk.Label() # top-level design label
        tooltips.set_tip(self.top_level_label, 'This is your top-level design'+
                        ' file. You can edit this in the Compile tab.')
        self.tool_path_entry = gtk.Entry() # synthesis tool path
        tooltips.set_tip(self.tool_path_entry, 'This is the path where the '+
                        'synthesis tools are installed.')
        self.tool_command_entry = gtk.Entry() # synthesis tool command
        tooltips.set_tip(self.tool_command_entry, 'This is the command to '+
                        'synthesis your design.')

        Hbox_syn1.pack_start(self.top_level_label, False, False, 3)
        Hbox_syn2.pack_start(gtk.Label('Synthesis tool path: '), False, False,3)
        #self.tool_path_entry.set_width_chars(90)
        Hbox_syn2.pack_start(self.tool_path_entry, True, True, 3)
        Hbox_syn3.pack_start(gtk.Label('Synthesis command: '), False, False,3)
        Hbox_syn3.pack_start(self.tool_command_entry, True, True, 3)
        Hbox_syn5.pack_start(gtk.Label('Device type: '), False, False,3)

        # populate FPGA family, device and package fiels
        self.ma=self.make_dropdown_menu(dev_manufacturer)
        self.fa=self.make_dropdown_menu(dev_family)
        self.de=self.make_dropdown_menu(dev_device)
        self.pa=self.make_dropdown_menu(dev_package)
        self.sp=self.make_dropdown_menu(dev_speed)
        self.ma.set_active(0)
        self.fa.set_active(0)
        self.de.set_active(0)
        self.pa.set_active(0)
        self.sp.set_active(3)
        self.de.set_wrap_width(3) # make a two-column dropdown menu

        # make small labels
        dev_lb1 = gtk.Label()
        dev_fixed = gtk.Fixed()
        dev_lb1.set_use_markup(gtk.TRUE)
        dev_lb1.set_markup('<span size="8000"'+
                           'foreground="#B5B2AC">'+
                           'manufacturer'+' '.join([' ' for i in range(19)])+\
                           'family'      +' '.join([' ' for i in range(19+8)])+\
                           'device'      +' '.join([' ' for i in range(19+8)])+\
                           'package'     +' '.join([' ' for i in range(19+6)])+\
                           'speed grade </span>')
        dev_fixed.put(dev_lb1,95,0)

        # put all together
        Hbox_syn5.pack_start(self.ma, False, False,3) # FPGA manufacturer
        Hbox_syn5.pack_start(self.fa, False, False,3) # FPGA family
        Hbox_syn5.pack_start(self.de, False, False,3) # FPGA device
        Hbox_syn5.pack_start(self.pa, False, False,3) # FPGA package
        Hbox_syn5.pack_start(self.sp, False, False,3) # FPGA speed grade
        Vbox_syn1.pack_start(Hbox_syn2, False, False, 5)
        Vbox_syn1.pack_start(Hbox_syn3, False, False, 10)
        Vbox_syn1.pack_start(Hbox_syn5, False, False, 0)
        Vbox_syn1.pack_start(dev_fixed, False, False, 0) # labels

        # whenever the family menu changed filter and redraw the device menu
        self.fa.connect("changed", self.filter_dropdown)
        self.filter_dropdown(self.window) # let's filter once at startup

        # Create and connect syn_button
        start_syn_button = gtk.Button('Run Synthesis')
        stop_syn_button = gtk.Button('Stop Synthesis')
        self.syn_p = None # this is the synthesize process handler
        start_syn_button.connect("clicked", self.syn_button_action, 'start')
        stop_syn_button.connect("clicked", self.syn_button_action, 'stop')
        Hbox_syn4.pack_start(start_syn_button, False, False, 3)
        Hbox_syn4.pack_start(stop_syn_button, False, False, 3)
        Vbox_syn1.pack_start(Hbox_syn4, False, False, 7)
        
        # load the whole Synthesize tab content
        notebook.append_page(Vbox_syn1, gtk.Label('Synthesize'))


        # make help tab (this is basically a web browser)
        scroller = gtk.ScrolledWindow()
        self.browser = webkit.WebView()
        self.browser.connect("load-progress-changed", self.load_progress_amount)
        self.browser.connect("load-started", self.load_started)
        self.browser.connect("load-finished", self.load_finished)
        self.browser.connect("load_committed", self.update_buttons)
        self.www_adr_bar = gtk.Entry()
        self.www_adr_bar.connect("activate", self.load_www)
        hlp_hbox = gtk.HBox()
        hlp_vbox = gtk.VBox()
        self.progress = gtk.ProgressBar()
        self.back_button = gtk.ToolButton(gtk.STOCK_GO_BACK)
        self.back_button.connect("clicked", self.go_back)
        self.forward_button = gtk.ToolButton(gtk.STOCK_GO_FORWARD)
        self.forward_button.connect("clicked", self.go_forward)
        home_button = gtk.ToolButton(gtk.STOCK_HOME)
        home_button.connect("clicked", self.go_home)
        # put help tab together
        hlp_hbox.pack_start(self.back_button, False, False,0)
        hlp_hbox.pack_start(self.forward_button, False, False)
        hlp_hbox.pack_start(home_button, False, False)
        hlp_hbox.pack_start(self.www_adr_bar, True, True)
        hlp_vbox.pack_start(hlp_hbox, False, False,5)
        hlp_vbox.pack_start(scroller, True, True)
        hlp_vbox.pack_start(self.progress, False, False, 5)
        scroller.add(self.browser)
        notebook.append_page(hlp_vbox, gtk.Label('Help')) # load

        self.back_button.set_sensitive(False)
        self.forward_button.set_sensitive(False)

        # make Preferences tab
        check_updates_button = gtk.Button('Check for Updates')
        pr_Hbox1 = gtk.HBox(False, 0)
        pr_Hbox1.pack_start(check_updates_button, False, False, 7)
        self.pr_pbar = gtk.ProgressBar(adjustment=None) # progress bar for "Check for Updates"
        pr_Hbox1.pack_start(self.pr_pbar, False, False, 7)
        self.pr_pbar.set_size_request(400,-1)
        #self.pr_pbar.set_text("you seem to be offline")
        #self.pr_pbar.set_fraction(0.2) 
        pr_Vbox1 = gtk.VBox(False, 0)
        pr_Vbox1.pack_start(pr_Hbox1, False, False, 7)
        notebook.append_page(pr_Vbox1, gtk.Label('Preferences'))
        check_updates_button.connect("clicked", self.update_boot)
        tooltips.set_tip(check_updates_button, "Check and download a new version of boot")

        ######## POPULATE COMPILE TAB ########
        # set current working directory as starting point and get
        # all VHDL files in it
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
             # let's just pick last vhdl file is wd
            best_guess_vhdl_file = os.path.join(wd,vhdl_files[-1])
            self.dir_entry.set_text(best_guess_vhdl_file)
            # possibly load the first "*_td.vhd*" file inside wd
            possible_vhdl_td = glob.glob(os.path.join(wd,'*_td.vhd')) + \
                               glob.glob(os.path.join(wd,'*_td.vhdl'))

            if len(possible_vhdl_td)!=0:
                self.dir_entry.set_text(os.path.join(wd,possible_vhdl_td[0]))

            # possibly load the first "*_tb.vhd*" file inside wd
            possible_vhdl_tb = glob.glob(os.path.join(wd,'*_tb.vhd')) + \
                               glob.glob(os.path.join(wd,'*_tb.vhdl'))

            if len(possible_vhdl_tb)!=0:
                self.dir_entry.set_text(os.path.join(wd,possible_vhdl_tb[0]))

        ######## POPULATE HELP TAB ########
        # load help content into Help tab (all taken from the web)
        default_www = 'http://www.freerangefactory.org/site/pmwiki.php/Main/BootDoc'
        self.www_adr_bar.set_text(default_www)
        self.browser.open(default_www)

        ######## POPULATE SYNTHESIZE TAB ########
        # just copy content from the compile dir entry field
        self.top_level_label.set_text('Top-level design: ' + \
                                      self.dir_entry.get_text())
        # default Xilinx XST synthesis tool path
        res = call('which xst'.split())
        if 0:
            self.tool_path_entry.set_text(res)
        else:
            self.tool_path_entry.set_text('you do not seem to have Xilinx ISE installed')


        # default xst command
        self.tool_command_entry.set_text('pwd')

        # load some data from a possible ~/.boot local file
        self.load_configuration_locally()

        # show all the widgets
        self.window.show_all()
#------------------------------ GUI CLASS END ----------------------------------

# turn on the GUI
def gui_up():
    gtk.main()
    return 0

# MAIN
def main():

    # create one pipe for communication between compilation/simulation process
    # an the GUI
    comp_comm_i, comp_comm_o = Pipe()

    # create and start process for compile and simulate task
    comp_prc = Process(target=comp_and_sim_proc, args=(comp_comm_o,))
    comp_prc.start()

    # make GUI object and start it.
    # the communication pipe is passed to the GUI
    my_gui = mk_gui()
    my_gui.add_conn(comp_comm_i)
    gui_up()

    # terminate all processes
    comp_prc.terminate()
    comp_prc.join()
    return 0

# to be executed when you call "./boot"
if __name__ == "__main__":

    # load parser for help options
    parser = argparse.ArgumentParser(
             description='Program to compile, simulate and synthesize your VHDL code.',
             epilog="Program made by: freerangefactory.org")

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




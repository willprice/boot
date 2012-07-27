import pygtk, gtk, gobject, glob, os, time
import ConfigParser, webkit
import vte

from subprocess import Popen, PIPE, STDOUT

import version, new_version
import tcl

pygtk.require('2.0')

import pango
import shlex
import editor
import devices

from pygments.lexers import PythonLexer
from pygments.styles.tango import TangoStyle
from pygments.token import Name, Keyword

gobject.threads_init()

# gui class for the main boot gui
class mk_gui:
    '''gui class for the main GUI of boot.
    '''

    # function to deleted or create a new file when top-level design file entry
    # is in focus and CTRL+D or CTRL+N is pressed
    def entry_keypress(self, widget, event):

        # detect CTRL+D key pressed
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

        # detect CTRL+N key pressed
        if event.keyval in (gtk.keysyms.N, gtk.keysyms.n) and \
                 event.state & gtk.gdk.CONTROL_MASK:

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

        # other key pressed
        else:
            print 'Key combination inactive.'
        return 0

    # Start and stop the compilation and/or simulation of your vhdl design
    def compileSimulateAction(self, widget, action):

        # working directory
        wd = os.path.dirname(os.path.realpath(self.dir_entry.get_text()))
        # top-level design file
        tld_file = os.path.basename(self.dir_entry.get_text())
        # simulation options
        sim_opt = self.sim_opt_entry.get_text()	

        # start compile process
        if action=='Compile':
            print 'Start compiling process'
            self.comm_i.send([wd, tld_file, self.GTKWAVE_COMM_SOCKET_ID, 
                              sim_opt, True, False]) # COMPILE

            self.btn_compile.set_label('Stop') # set button to "Stop"

        # start compile process
        if action=='Compile & Simulate':
            print 'Start compiling process'
            self.comm_i.send([wd, tld_file, self.GTKWAVE_COMM_SOCKET_ID, 
                              sim_opt, True, True]) # COMPILE AND SIMLATE

            self.btn_compile.set_label('Stop') # set button to "Stop"

        # stop compile process
        if action=='Stop':
            print 'Stop compiling process (not implemented)'
            # terminate all child processes inside compiling process
            # TODO THE STOP BUTTON IS NOT IMPLEMENTED YET
            self.btn_compile.set_label('Compile')

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

    # delete and kill main window
    def delete(self, widget, event=None):
        gtk.main_quit()
        return False

    # method to attach pipes to the GUI
    def add_conn(self, compute_prc, comm_i):
        # compute process
        self.compute_prc = compute_prc
        # pipes for compilation and simulation processes
        self.comm_i = comm_i
        # attach the pipe input to the method "update_gui"
        # inspired by: http://haltcondition.net/?p=2319
        fd = comm_i.fileno()
        gobject.io_add_watch(fd, gobject.IO_IN, self.update_gui)
        return 0

    # method to update GUI with pipe information
    def update_gui(self, fd, cond):
        #global GUI_COMPILATION_ERROR

        # update compiling tab
        val = self.comm_i.recv()
        self.make_pretty_txt(self, val, self.comp_textbuffer)
        if 'Begin compiling'in val:
            self.comp_bar_go = True         # compile bar running
            self.comp_bar.set_text("Compiling...")
            #GUI_COMPILATION_ERROR = False
        elif 'compilation error' in val:
            self.comp_bar_go = False        # compile bar off
            self.comp_bar.set_text("Compilation Error.")
            self.comp_bar.set_fraction(0.0)
            #GUI_COMPILATION_ERROR = True
            print 'Compilation error.'
        elif 'End compiling' in val:
            self.comp_bar_go = False        # compile bar off
            self.comp_bar.set_text("Compilation Successful.")
            self.comp_bar.set_fraction(0.0)
            self.btn_compile.set_label('Compile') # set button to "compile"
            print 'Compilation process ended.'
        #elif  'End processing'in val and (not GUI_COMPILATION_ERROR):
        elif  'End processing'in val:
            self.comp_bar_go = False         # compile bar off
            self.comp_bar.set_text("Compilation Successful.")
            self.comp_bar.set_fraction(1.0)
            print 'Compiled successfully.'
        elif 'CLEAR ALL' in val:
            self.comp_textbuffer.set_text('') # clear screen
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
        config.set('boot', 'version', version.boot_version)
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
    def load_local_configuration_file(self):
        conf_file = os.path.join(os.environ['HOME'],'.boot')
        if os.path.isfile(conf_file):
            print 'Loading some parameters from local "~/.boot" file' 
            config = ConfigParser.ConfigParser()
            config.readfp(open(conf_file))

            _ma = config.get('Last parameters', 'manufacturer')
            _fa = config.get('Last parameters', 'family')
            _de = config.get('Last parameters', 'device')
            _pa = config.get('Last parameters', 'package')
            _sp = config.get('Last parameters', 'speed grade')

            sim_opt = config.get('Last parameters', 'simulation options')
            syn_tool_path = config.get('Last parameters', 'synthesis tool path')
            syn_comm = config.get('Last parameters', 'synthesis command')

            # this will set the device menu item to the one in the "~/.boot" file
            for x,y in enumerate(self.ma.get_model()):
                if y[0] == _ma:
                    self.ma.set_active(x)
            for x,y in enumerate(self.fa.get_model()):
                if y[0] == _fa:
                    self.fa.set_active(x)
            for x,y in enumerate(self.de.get_model()):
                if y[0] == _de:
                    self.de.set_active(x)
            for x,y in enumerate(self.pa.get_model()):
                if y[0] == _pa:
                    self.pa.set_active(x)
            for x,y in enumerate(self.sp.get_model()):
                if y[0] == _sp:
                    self.sp.set_active(x)

            # set synthesis variables like the ones in the "~/.boot" file
            self.sim_opt_entry.set_text(sim_opt)
            self.tool_path_entry.set_text(syn_tool_path)
            self.tool_command_entry.set_text(syn_comm)
        return 0

    # Generate and save synthesis script
    def gen_syn_script_button_action(self, widget, action):

        # get information from Synthesis tab
        tl   = os.path.basename(self.dir_entry.get_text())
        tl = tl.split('.')[0] # strip ".vhdl" extension

        # working directory
        wd = os.path.dirname(os.path.realpath(self.dir_entry.get_text()))

        # this is where all synthesis files will go
        syn_out_dir = os.path.join(wd, 'build')

        # work out all files in the current working folder
        files = glob.glob(os.path.join(wd,'*.vhd')) + \
                         glob.glob(os.path.join(wd,'*.vhdl'))

        # strip away path from each file
        files = [os.path.basename(x) for x in files]

        # take away all files with "_tb" in its name
        # in fact test-bench files will not be synthesized
        for x in files:
            if '_tb' in x: files.remove(x) 
        
        # find constrain files
        constraints_file = glob.glob(os.path.join(wd,'*.ucf'))

        print 'Synthesis script about to be generated.'
        print 'top-level design:', tl
        print 'vhdl file list:', files
        print 'Constrains file:', constraints_file

        # get device parameters from Synthesis tab
        ma = self.ma.get_model()[self.ma.get_active()][0]
        fa = self.fa.get_model()[self.fa.get_active()][0]
        de = self.de.get_model()[self.de.get_active()][0]
        pa = self.pa.get_model()[self.pa.get_active()][0]
        sp = self.sp.get_model()[self.sp.get_active()][0]

        # Creating synthesis folder
        if os.path.isdir(syn_out_dir):
            pass
        else:
            os.path.os.mkdir(syn_out_dir)

        # Generating and saving synthesis script
        try:
            if tcl.make_xilinx(syn_out_dir, tl, files, constraints_file, 
                                  fa, de, pa, sp):
                print 'Synthesis script generation process failed.'
                return 1
            print 'Xilinx synthesis script generated.'

            _start = self.syn_textbuffer.get_end_iter()
            _txt = 'Xilinx synthesis script generated.\n'
            self.syn_textbuffer.insert_with_tags(_start,_txt)

            # update the synthesis command field
            _txt = 'xtclsh src/build/xil_syn_script.tcl'
            self.tool_command_entry.set_text(_txt)
        except:
            print 'Problems in saving the Xilinx synthesis script.'
            print 'Maybe you have rights permission problems.'
            return 1
        return 0

    # open the default editor and show a file
    def open_in_editor(self, label, uri):
        wd = os.path.dirname(os.path.realpath(self.dir_entry.get_text()))
        tld_file = os.path.basename(self.dir_entry.get_text())
        _fl=''

        if 'synthesis_report' in uri:
            tld = tld_file.split('.')[0]
            _fl = os.path.join(wd,'build',tld+'.syr')
        if 'xtclsh_script' in uri:
             _fl = os.path.join(wd,'build','xil_syn_script.tcl')

        if os.path.isfile(_fl):
                try:
                    print 'Opening the file in boot text viewer.'
                    editor.text_editor(_fl).start()
                except:
                    print 'Problems in loading the file'

        return True # to indicate that we handled the link request

    # watchdog to disconnect synthesis process pipes when the synthesis
    # process end naturally 
    def syn_watchdog(self,w):
        if type(self.syn_p) is Popen and self.syn_p.poll() == None:
            # change button label
            self.start_stop_syn_button.set_label('Stop Synthesis')
            self.syn_spinner.start() # make the synthesis wheen spin
            return True # process exista and still running
        else:
            gobject.source_remove(self.g_syn_id)
            print 'Synthesis process naturally ended and pipe closed.'
            # change button label
            self.start_stop_syn_button.set_label('Start Synthesis')
            self.syn_spinner.stop() # make the synthesis wheen stop spinning
            return False # this will stop the "gobject.timeout_add"

    # Start and stop the Synthesis of your vhdl design
    def syn_button_action(self, widget, action):
        
        # it is necessary to read the status of the button every time
        action = self.start_stop_syn_button.get_label()

        # get information from Synthesis tab
        tl = self.dir_entry.get_text()
        syn_path = self.tool_path_entry.get_text()
        syn_cmd = self.tool_command_entry.get_text()
        wd = os.path.dirname(os.path.realpath(self.dir_entry.get_text()))

        # work in progress warning window
        #self.on_warn('Sorry mate, this feature is not implemented yet.')

        # execute stuff
        if action=='Start Synthesis':

            #save some parameters on local "~/.boot" file
            self.save_configuration_locally()
            
            # if the synthesis process exists already and has not terminated, exit
            if self.syn_p!=None and self.syn_p.returncode == None:
                print 'Synthesis process not terminated yet. Exiting'
                return 0
            print 'Starting synthesis process.'
            self.syn_textbuffer.set_text('Synthesis process output window.\n')

            # delete ISE project inside the folder "build"
            # this will most probably guarantee that synthesis will start 
            # from the beginning
            all_unwanted_fls = glob.glob(os.path.join(wd,'build','*.xise'))
            for fl in all_unwanted_fls:
                os.remove(fl)

            # execute the "source" command (using ".") and also
            command = ['bash','-c',syn_path + '>>/dev/null; env']
            proc = Popen(command, stdout = PIPE)

            # import and apply the new environment values using "os.environ"
            for line in proc.stdout:
                (key, _, value) = line.rstrip('\n').partition("=")
                os.environ[key] = value
            proc.communicate() # this waits for the process "proc" to terminate
            #pprint.pprint(dict(os.environ))

            # change directory and run synthesis script
            cmd = syn_cmd
            #cmd = 'xtclsh src/build/xil_syn_script.tcl'
            #cmd = "find / -name 't'"
            # TODO: Note that maybe bufsize=10 could be 
            #       problematic (lots of CPU used)
            try:
                self.syn_p = Popen(shlex.split(cmd), bufsize=10,
                                   stdout=PIPE, stderr=STDOUT)
                print 'New Synthesis process ID:',self.syn_p.pid
            except:
                print 'Process "xtclsh" cannot start.'
                _start = self.syn_textbuffer.get_end_iter()
                self.syn_textbuffer.insert_with_tags(_start,
                'Process "xtclsh" cannot start. Maybe you do not have '+\
                'Xilinx ISE installed in your machine.\n')
                return 0
            
            # now the button to start the synthesis will become the button
            # to stop the synthesis by changing its label
            # change button label
            self.start_stop_syn_button.set_label('Stop Synthesis')

            # let's now redirect "self.syn_p" stdout to a GUI method
            # using "gobject".
            # let's deleted it if it already exist
            if self.g_syn_id != None:
                gobject.source_remove(self.g_syn_id)
            self.g_syn_id = gobject.io_add_watch(self.syn_p.stdout,
                                                 gobject.IO_IN,
                                                 self.write_to_syn_output)  

            # now that the synthesis process has started let's create a
            # second process that kills it
            # and disconnects it pipe as soon as the process ends.
            gobject.timeout_add(200, self.syn_watchdog, self)
         
            # done !

        elif action == 'Stop Synthesis':

            # delete gobject for synthesis process communication
            if self.g_syn_id != None:
                gobject.source_remove(self.g_syn_id)

            # if the synthesis process exists and is running kill it and
            # check the existence of synthesis process
            if type(self.syn_p) is Popen:
                try:
                    print 'Current Synthesis process ID:',self.syn_p.pid
                    self.syn_p.kill() # kill synthesis process
                    while self.syn_p.poll() == None:
                        time.sleep(0.2)
                    print 'Synthesis process stopped.'
                    # change button label
                    self.start_stop_syn_button.set_label('Start Synthesis')
                except:
                    print 'Synthesis process already killed.'
                    # change button label
                    self.start_stop_syn_button.set_label('Start Synthesis')
                    
        else:
            print 'Wrong synthesis command.'
        return 0

    # this class add more keywords that will be colored in blu.
    # TODO find a way to color stuff in red.
    class MyPythonLexer(PythonLexer):
        EXTRA_KEYWORDS = ['Begin', 'End', 'simulation', 'compiling','error','No'
                          'processing', 'completed','successfully','warning',
                          'Completed','failed']

        def get_tokens_unprocessed(self, text):
            for index, token, value in PythonLexer.get_tokens_unprocessed(self,
                                                                          text):
                if token is Name and value in self.EXTRA_KEYWORDS:
                    yield index, Keyword.Pseudo, value
                else:
                    yield index, token, value

    # this method will style each line that gets displayed in the
    # text output window, it is used for the synthesis output
    # and for the compile output
    def make_pretty_txt(self, widget, _txt, _buff):

        STYLE = TangoStyle
        styles = {}
        #for token, value in PythonLexer().get_tokens(_txt):
        for token, value in self.MyPythonLexer().get_tokens(_txt):
            while not STYLE.styles_token(token) and token.parent:
                token = token.parent
            if token not in styles:
                styles[token] = _buff.create_tag()
            start = _buff.get_end_iter()
            _buff.insert_with_tags(start, value.encode('utf-8'), styles[token])

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
        return 0

    # this method allows data in to get directed to the synthesis output window
    def write_to_syn_output(self, fd, condition):
        if condition == gobject.IO_IN:
            #char = fd.read(1) # read one byte at the time
            char = fd.readline()
            #self.syn_textbuffer.insert_at_cursor(char)
            self.make_pretty_txt(self, char, self.syn_textbuffer)
            return True
        else:
            return False

    # populate the FPGA device fields
    def make_dropdown_menu(self, data_in):
        # create a gtk.trees with data_in in it
        # note how only the last element of data_in is displayed
        store = gtk.TreeStore(str)
        for x in data_in:
            store.append(None, [x])
            #store.append(None, [x.split()[-1]])

        # create a drop-down menu with tree in it
        combo = gtk.ComboBox(store)
        combo_cell_text = gtk.CellRendererText()
        combo.pack_start(combo_cell_text, True)
        combo.add_attribute(combo_cell_text, "text", 0)
        combo.set_size_request(142, -1)
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
        for x in devices.dev_device:
            if current_fa in x:
                y=x.split()[1]
                model.append(None, [y])
        self.de.set_model(model)

        # set the first one 
        self.de.set_active(0)
        return 0

    # set boot to its default settings by deleting ~/.boot file
    def set_default_boot(self, widget):
        try:
            homedir = os.path.expanduser("~")
            os.remove(os.path.join(homedir,'.boot'))
            print 'Local configuration file: ~/.boot deleted.'
        except:
            print 'Nothing to do.'
        _txt = 'Done, you should now restart boot.'
        self.set_default_button_label.set_text(_txt)
        return 0

    # check for and new version of "boot"
    def check_for_new_ver(self, widget):
        self.update_boot_msg.set_text('')
        _answer = new_version.check_on_pypi()
        print _answer
        self.update_boot_msg.set_text(_answer)
        return 0

    # set of methods for the help tab browser
    def go_back(self, widget, data=None):
        self.browser.go_back()
    def go_forward(self, widget, data=None):
        self.browser.go_forward()
    def go_home(self, widget, data=None):
        _txt = 'http://www.freerangefactory.org/site/pmwiki.php/Main/BootDoc'
        self.browser.open(_txt)
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

    # re-scroll the synthesis text output window so that
    # new text is always shown
    def syn_rescroll(self, widget):
        self.vadj.set_value(self.vadj.upper-self.vadj.page_size)
        self.syn_scroller.set_vadjustment(self.vadj)

    # re-scroll the compile text output window so that
    # new text is always shown
    def comp_rescroll(self, widget):
        self.comp_vadj.set_value(self.comp_vadj.upper-self.comp_vadj.page_size)
        self.comp_scroller.set_vadjustment(self.comp_vadj)

    # Update the value of the compile progress bar so that we get
    # some movement
    def comp_bar_timeout(self,pbobj):
        if self.comp_bar_go: # bar enabled
            pbobj.comp_bar.pulse()
        else: # bar disabled
            pass
        return True

    # Clean up allocated memory and remove the compile progress bar timer
    def destroy_progress(self, widget, data=None):
        gobject.source_remove(self.comp_bar_timer)
        self.comp_bar_timer = 0
        gtk.main_quit()

    # constructor for the whole GUI
    def __init__(self):

        # make the main window
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        #self.window.connect("delete_event", self.delete)
        self.window.connect("destroy", self.destroy_progress)
        self.window.set_border_width(2)
        #self.window.set_size_request(920, 500)
        self.window.set_size_request(920, 600)
        _txt = 'freerangefactory.org - boot ver. ' + version.boot_version
        self.window.set_title(_txt)

        # make a 1X1 table to put the tabs in (this table is not really needed)
        table = gtk.Table(rows=1, columns=1, homogeneous=False)
        #self.window.add(table)

        # make tool-tip object
        tooltips = gtk.Tooltips()


       ######## TERMINAL TAB ##########
        # make terminal
        terminal = vte.Terminal()
        terminal.connect ("child-exited", lambda term: gtk.main_quit())
        terminal.fork_command()

        # style the terminal
        colours = [(0x2e2e, 0x3434, 0x3636),(0xcccc, 0x0000, 0x0000),
                   (0x4e4e, 0x9a9a, 0x0606),(0xc4c4, 0xa0a0, 0x0000),
                   (0x3434, 0x6565, 0xa4a4),(0x7575, 0x5050, 0x7b7b),
                   (0x0606, 0x9820, 0x9a9a),(0xd3d3, 0xd7d7, 0xcfcf),
                   (0x5555, 0x5757, 0x5353),(0xefef, 0x2929, 0x2929),
                   (0x8a8a, 0xe2e2, 0x3434),(0xfcfc, 0xe9e9, 0x4f4f),
                   (0x7272, 0x9f9f, 0xcfcf),(0xadad, 0x7f7f, 0xa8a8),
                   (0x3434, 0xe2e2, 0xe2e2),(0xeeee, 0xeeee, 0xecec)]
        foreground = gtk.gdk.Color(0, 0, 0)
        background = gtk.gdk.Color(0xffff, 0xffff, 0xffff)
        palette = [gtk.gdk.Color(*colour) for colour in colours]
        terminal.set_colors(foreground, background, palette)

        # put the terminal in a scrollable window
        terminal_window = gtk.ScrolledWindow()
        terminal_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        terminal_window.add(terminal)

        # make a resizable panel
        vpaned = gtk.VPaned()
        vpaned.pack1(terminal_window, shrink=True)
        vpaned.pack2(table, shrink=True)
        self.window.add(vpaned)
        
        _txt = 'File manager and text editor. Slide down to open.'
        tooltips.set_tip(vpaned, _txt)

        # Create a notebook and place it inside the table
        notebook = gtk.Notebook()
        notebook.set_tab_pos(gtk.POS_TOP)
        table.attach(child=notebook, left_attach=0, right_attach=1, 
                     top_attach=0, bottom_attach=1, xpadding=0, ypadding=0)

        ######## COMPILE TAB ##########
        # LOAD CONTENT into Compile tab
        Vbox1 = gtk.VBox(False, 0)
        notebook.append_page(Vbox1, gtk.Label('Compile')) # load

        # compile output text area
        self.comp_scroller = gtk.ScrolledWindow()
        self.comp_scroller.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        self.comp_scroller.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        comp_out = gtk.TextView()
        comp_out.set_left_margin (10);
        comp_out.set_right_margin (10);
        comp_out.set_editable(False)
        self.comp_textbuffer = comp_out.get_buffer()
        self.comp_scroller.add(comp_out)
        _txt ='For the synthesis of your design select your VHDL top-level'+\
               'design file.\nIf you are interested in running a simulation'+\
               'of your design, select instead your test-bench file.\n\n'+\
               'For any addtional help please consult the Help Tab.'
        self.comp_textbuffer.set_text(_txt) 

        # style the synthesis output text area
        comp_out.modify_font(pango.FontDescription('monospace 9'))
    
        # let's keep the new text in "comp_textbuffer" always in view
        self.comp_vadj = self.comp_scroller.get_vadjustment()
        self.comp_vadj.connect('changed',self.comp_rescroll)

        # make directory entry
        self.dir_entry = gtk.Entry()
        tooltips.set_tip(self.dir_entry, 
        'Here you select the top-level design file or the test-bench file.\n'+
        'The following shortcuts are also available:\n' +
        'CTRL-N:  create a new file.\n' +
        'CTRL-D:  delete current file.\n')

        # let's trigger an action when the text changes
        #self.dir_entry.connect("changed", self.dir_entry_changed)

        # let's trigger a file action when top-level design file entry
        # is in focus and a certain key combination is pressed
        self.dir_entry.connect('key-press-event', self.entry_keypress)

        # make select top-level design file button
        self.img_ind = gtk.Image()
        self.img_ind.set_from_stock(gtk.STOCK_INDEX, gtk.ICON_SIZE_BUTTON)
        btn_ind = gtk.Button()
        btn_ind.add(self.img_ind)
        btn_ind.connect("clicked", self.select_file)
        tooltips.set_tip(btn_ind, 
                         "Select top-level design file or test-bench file.")

        # compile button
        self.btn_compile = gtk.Button('Compile')
        self.btn_compile.connect("clicked",self.compileSimulateAction,'Compile')
        tooltips.set_tip(self.btn_compile,'Check and compile your design.')
     
        # put stuff together in the window
        Hbox1 = gtk.HBox(False, 0)
        Hbox1.pack_start(btn_ind, False, False, 0)
        Hbox1.pack_start(self.dir_entry, True, True,0)
        Hbox1.pack_start(self.btn_compile, False, False, 0)

        self.comp_bar = gtk.ProgressBar()
        self.comp_bar.set_text("sleeping")
        self.comp_bar.set_pulse_step(0.04)
        self.comp_bar.set_fraction(0.1) 
        self.comp_bar_go = False  # set compile progress bar off
        self.comp_bar.set_visible(False) # hide compile progress bar 
        # timer for comp_bar
        self.comp_bar_timer =gobject.timeout_add(100,self.comp_bar_timeout,self)

        Vbox1.pack_start(Hbox1, False, False, 0)

        # make a small label
        lb1 = gtk.Label()
        fixed1 = gtk.Fixed()

        lb1.set_use_markup(gtk.TRUE)
        lb1.set_markup('<span size="8000" \
                        foreground="#B5B2AC">top-level VHDL design file</span>')
        fixed1.put(lb1,35,0)

        # make check box "auto compile"
        self.chk1 = gtk.CheckButton("auto")
        self.chk1.set_active(False)
        self.chk1.set_sensitive(False)
        tooltips.set_tip(self.chk1,'Automatically compile your design '+\
                                 'every time a vhdl file in "src/" is modified')

        # let's trigger an action when the check box changes
        #self.chk1.connect("clicked", self.run_compile_and_sim, False)

        fixed2 = gtk.Fixed()
        fixed2.put(self.chk1,-70,-1)
        Hbox3 = gtk.HBox(False, 0)

        Hbox3.pack_start(fixed1, False, False, 0)
        Hbox3.pack_end(fixed2, False, False, 0)
        Vbox1.pack_start(Hbox3, False, False, 0)

        # add compile notification area to the compile tab and progress bar
        Vbox1.pack_start(self.comp_scroller, True, True, 2)
        Vbox1.pack_start(self.comp_bar, False, False, 0)

       ######## SIMULATE TAB ##########
        # make socket for boot => gtkwave communication
        self.my_socket = gtk.Socket()

        # make Simulate tab and connect to socket
        Vbox2 = gtk.VBox(False, 0)
        notebook.append_page(Vbox2, gtk.Label('Simulate')) # load vbox into tab

        # compile and simulate button
        self.btn_compileAndSimulate = gtk.Button('Compile & Simulate')
        self.btn_compileAndSimulate.connect("clicked", 
                                            self.compileSimulateAction, 
                                            'Compile & Simulate')
        tooltips.set_tip(self.btn_compileAndSimulate,
                         'Check, compile and simulate your VHDL design.')

        # load some fields into Simulate tab
        Hbox3 = gtk.HBox(False, 0)
        self.sim_opt_entry = gtk.Entry()# make simulation option field entry
        tooltips.set_tip(self.sim_opt_entry, 'Enter simulation options.')
        self.sim_opt_entry.set_text('--stop-time=200ns')
        sim_opt_label = gtk.Label("Simulation options: ") # text label
        Hbox3.pack_start(sim_opt_label, False, False, 2)
        Hbox3.pack_start(self.sim_opt_entry, True, True, 2)
        Hbox3.pack_end(self.btn_compileAndSimulate, False, False, 2)

        Vbox2.pack_start(Hbox3, False, False, 0)

        # make check box "auto compile & simulate"
        self.chk2 = gtk.CheckButton("auto")
        self.chk2.set_active(False)
        self.chk2.set_sensitive(False)
        tooltips.set_tip(self.chk2, 
                         'Automatically compile and simulate your design '+\
                         'every time a vhdl file in "src/" is modified')

        # let's trigger an action when the check box changes
        #self.chk2.connect("clicked", self.run_compile_and_sim, False)

        fixed3 = gtk.Fixed()
        fixed3.put(self.chk2,-145,-1)
        Hbox4 = gtk.HBox(False, 0)
        Hbox4.pack_end(fixed3, False, False, 0)
        Vbox2.pack_start(Hbox4, False, False, 0)


        # let's trigger an action when the simulation option field changes
        #self.sim_opt_entry.connect("activate", self.run_compile_and_sim, True)

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

        ######## SYNTHESIZE TAB ##########
        # make Synthesize tab 
        Hbox_syn1 = gtk.HBox(False, 0)
        Hbox_syn2 = gtk.HBox(False, 0)
        Hbox_syn3 = gtk.HBox(False, 0)
        Hbox_syn4 = gtk.HBox(False, 0)
        Hbox_syn5 = gtk.HBox(False, 0)
        Vbox_syn1 = gtk.VBox(False, 0)
        Vbox_syn1.set_border_width(10)
        self.top_level_label = gtk.Label() # top-level design label
        tooltips.set_tip(self.top_level_label, 'This is your top-level design '+
                        'file. You can edit this in the Compile tab.')
        self.tool_path_entry = gtk.Entry() # synthesis tool path
        tooltips.set_tip(self.tool_path_entry, 'This is the path where the '+
                        'synthesis tools are installed.')
        self.tool_command_entry = gtk.Entry() # synthesis tool command
        tooltips.set_tip(self.tool_command_entry, 'This is the command to '+
                        'synthesis your design.')

        Hbox_syn1.pack_start(self.top_level_label, False, False, 3)
        Hbox_syn2.pack_start(gtk.Label('Synthesis tool path setting command: '),
                             False, False,3)

        #self.tool_path_entry.set_width_chars(90)
        Hbox_syn2.pack_start(self.tool_path_entry, True, True, 3)
        Hbox_syn3.pack_start(gtk.Label('Synthesis command: '), False, False,3)
        Hbox_syn3.pack_start(self.tool_command_entry, True, True, 3)
        Hbox_syn5.pack_start(gtk.Label('Device type: '), False, False,3)

        # populate FPGA family, device and package fields
        self.ma = self.make_dropdown_menu(devices.dev_manufacturer)
        self.fa = self.make_dropdown_menu(devices.dev_family)
        self.de = self.make_dropdown_menu(devices.dev_device)
        self.pa = self.make_dropdown_menu(devices.dev_package)
        self.sp = self.make_dropdown_menu(devices.dev_speed)
        # set the default device values
        self.ma.set_active(0)
        self.fa.set_active(0)
        #self.de.set_active(0)
        self.pa.set_active(4)
        self.sp.set_active(3)
         # make some menu multi column
        self.de.set_wrap_width(3)
        self.pa.set_wrap_width(7)
        self.sp.set_wrap_width(2)

        # make small labels
        dev_lb1 = gtk.Label()
        dev_fixed = gtk.Fixed()
        dev_lb1.set_use_markup(gtk.TRUE)
        dev_lb1.set_markup('<span size="8000"'+
                           'foreground="#B5B2AC">'+
                           'manufacturer'+' '.join([' ' for i in range(22)])+\
                           'family'      +' '.join([' ' for i in range(22+8)])+\
                           'device'      +' '.join([' ' for i in range(22+8)])+\
                           'package'     +' '.join([' ' for i in range(22+6)])+\
                           'speed grade </span>')
        dev_fixed.put(dev_lb1,95,0)

        # page synthesis output text area
        self.syn_scroller = gtk.ScrolledWindow()
        self.syn_scroller.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        self.syn_scroller.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        syn_out = gtk.TextView()
        syn_out.set_left_margin (10);
        syn_out.set_right_margin (10);
        syn_out.set_editable(False)
        self.syn_textbuffer = syn_out.get_buffer()
        self.syn_scroller.add(syn_out)
        self.syn_textbuffer.set_text('ready to go!\n') 

        # style the synthesis output text area
        syn_out.modify_font(pango.FontDescription('monospace 9'))
    
        # let's keep the new text in "syn_textbuffer" always in view
        self.vadj = self.syn_scroller.get_vadjustment()
        self.vadj.connect('changed',self.syn_rescroll)

        # put all together
        Hbox_syn5.pack_start(self.ma, False, False,3) # FPGA manufacturer
        Hbox_syn5.pack_start(self.fa, False, False,3) # FPGA family
        Hbox_syn5.pack_start(self.de, False, False,3) # FPGA device
        Hbox_syn5.pack_start(self.pa, False, False,3) # FPGA package
        Hbox_syn5.pack_start(self.sp, False, False,3) # FPGA speed grade
        Vbox_syn1.pack_start(Hbox_syn1, False, False, 5)

        # make line separator
        separator = gtk.HSeparator()
        Vbox_syn1.pack_start(separator, False, False, 10)

        Vbox_syn1.pack_start(Hbox_syn2, False, False, 5)
        Vbox_syn1.pack_start(Hbox_syn3, False, False, 10)
        Vbox_syn1.pack_start(Hbox_syn5, False, False, 0)
        Vbox_syn1.pack_start(dev_fixed, False, False, 0) # labels

        # whenever the family menu changed filter and redraw the device menu
        self.fa.connect("changed", self.filter_dropdown)
        self.filter_dropdown(self.window) # let's filter once at startup

        # Create and connect syn_button
        self.start_stop_syn_button = gtk.Button('Start Synthesis')
        gen_syn_script_button = gtk.Button('Generate Script')
        self.syn_spinner = gtk.Spinner()

        # this is the synthesize process handler
        self.syn_p = None

        # this is the gobject for communication with the synthesis window
        self.g_syn_id = None

        self.start_stop_syn_button.connect("clicked", 
                                           self.syn_button_action, 
                                           self.start_stop_syn_button.get_label())
        gen_syn_script_button.connect("clicked", 
                                      self.gen_syn_script_button_action,
                                      'gen_script')

        # add Synthesis Report label that opens src\build\counter_top.syr
        syn_report_lb = gtk.Label()
        syn_report_lb_fixed = gtk.Fixed()
        syn_report_lb.modify_font(pango.FontDescription("monospace 9"))
        _txt = '<a href="xtclsh_script">xtclsh script</a>'+\
               '<a href="synthesis_report">synthesis report</a>'
        syn_report_lb.set_markup(_txt)
        syn_report_lb.connect('activate-link', self.open_in_editor)
        syn_report_lb_fixed.put(syn_report_lb,0,15)

        # pack things together
        Hbox_syn4.pack_start(gen_syn_script_button, False, False, 3)
        Hbox_syn4.pack_start(self.start_stop_syn_button, False, False, 3)
        Hbox_syn4.pack_start(self.syn_spinner, False, False, 0)
        Hbox_syn4.pack_end(syn_report_lb_fixed, False, False, 3)
        Vbox_syn1.pack_start(Hbox_syn4, False, False, 7)
        Vbox_syn1.pack_start(self.syn_scroller, True, True)

        # load the whole Synthesize tab content
        notebook.append_page(Vbox_syn1, gtk.Label('Synthesize'))

        ######## HELP TAB ##########
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

        ######## PREFERENCE TAB ##########
        # make Preferences tab
        check_updates_button = gtk.Button('Check for Updates')
        set_default_button = gtk.Button('Set Default')
        _txt = 'Reset boot to its default configuration.'
        self.set_default_button_label = gtk.Label(_txt)
        pr_Hbox1 = gtk.HBox(False, 0)
        pr_Hbox2 = gtk.HBox(False, 0)
        pr_Hbox1.pack_start(check_updates_button, False, False, 7)
        pr_Hbox2.pack_start(set_default_button, False, False, 7)
        pr_Hbox2.pack_start(self.set_default_button_label, False, False, 2)
        self.update_boot_msg = gtk.Label('')
        pr_Hbox1.pack_start(self.update_boot_msg, False, False, 7)

        pr_Vbox1 = gtk.VBox(False, 0)
        pr_Vbox1.pack_start(pr_Hbox1, False, False, 7)
        pr_Vbox1.pack_start(pr_Hbox2, False, False, 7)
        notebook.append_page(pr_Vbox1, gtk.Label('Preferences'))
        check_updates_button.connect("clicked", self.check_for_new_ver)
        set_default_button.connect("clicked", self.set_default_boot)
        tooltips.set_tip(check_updates_button, "Download a new version of boot")
        tooltips.set_tip(set_default_button, "Set boot to its default status")

        ######## LIST OF ACTIONS TO PERFORM WHEN THE GUI STARTS UP ##########

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

        print 'Current working directory:', wd
        self.dir_entry.set_text(wd)
        
        # load vhdl file by picking the last .vhd* file 
        if len(vhdl_files)!=0:
             # let's just pick last vhdl file is wd
            best_guess_vhdl_file = os.path.join(wd,vhdl_files[-1])
            self.dir_entry.set_text(best_guess_vhdl_file)
            # possibly load the first "*_top.vhd*" file inside wd
            possible_vhdl_top = glob.glob(os.path.join(wd,'*_top.vhd')) + \
                               glob.glob(os.path.join(wd,'*_top.vhdl'))

            if len(possible_vhdl_top)!=0:
                self.dir_entry.set_text(os.path.join(wd,possible_vhdl_top[0]))

            # possibly load the first "*_tb.vhd*" file inside wd
            possible_vhdl_tb = glob.glob(os.path.join(wd,'*_tb.vhd')) + \
                               glob.glob(os.path.join(wd,'*_tb.vhdl'))

            if len(possible_vhdl_tb)!=0:
                self.dir_entry.set_text(os.path.join(wd,possible_vhdl_tb[0]))

        ######## POPULATE HELP TAB ########
        # load help content into Help tab (all taken from the web)
        _txt = 'http://www.freerangefactory.org/site/pmwiki.php/Main/BootDoc'
        default_www = _txt
        self.www_adr_bar.set_text(default_www)
        self.browser.open(default_www)

        ######## POPULATE SYNTHESIZE TAB ########
        # just copy content from the compile dir entry field
        self.top_level_label.set_text('Top-level design: ' + \
                                      self.dir_entry.get_text())

        # try to guess the Xilinx xtclsh synthesis tool path by checking
        # Xilinx ISE environment variables and 
        # generate a "source" command with "."
        try:
            answer = os.environ.get("XILINX_DIR")
            cmd = 'source ' + answer + '/settings64.sh'
            self.tool_path_entry.set_text(cmd)
            print 'Xilinx ISE software too detected at:', answer
        except:
            # set the kind of default Xilinx ISE 
            # path (maybe we could try to search for it)
            _txt = 'source /opt/Xilinx/13.2/ISE_DS/settings64.sh'
            self.tool_path_entry.set_text(_txt)

        # default xtclsh command
        self.tool_command_entry.set_text('Not set')

        # load data from a possible ~/.boot local file
        # NOTE: this will overwrite lots of GUI variables.
        self.load_local_configuration_file()

        # show all the widgets
        self.window.show_all()
	





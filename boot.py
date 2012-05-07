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

__version__ = 0.16
__author__ = 'Fabrizio Tappero'

import pygtk, gtk, gobject, glob, os, time, sys, argparse
import ConfigParser, webkit, httplib, pprint

from gtk import gdk
pygtk.require('2.0')
from subprocess import call, Popen, PIPE, STDOUT
from multiprocessing import Process, Pipe
import gobject, pango

# Xilinx device data
# # http://www.xilinx.com/support/index.htm
dev_manufacturer  = ['Xilinx', 'Altera', 'Actel'] 
dev_family  = ['Spartan6','Spartan3','Spartan3A','Spartan3E','Artix','Kintex',
'Virtex4','Virtex5','Virtex6','Virtex7','Zynq','CoolRunner','XC9500X']
dev_device=['Zynq7000 XC7Z010','Zynq7000 XC7Z020','Zynq7000 XC7Z030','Zynq7000 XC7Z045','Artix7 XC7A100T','Artix7 XC7A200T',
'Artix7 XC7A350T','Kintex7 XC7K70T','Kintex7 XC7K160T','Kintex7 XC7K325T','Kintex7 XC7K355T','Kintex7 XC7K410T','Kintex7 XC7K420T',
'Kintex7 XC7K480T','Virtex7 XC7V585T','Virtex7 XC7V1500T','Virtex7 XC7V2000T','Virtex7 XC7VX330T','Virtex7 XC7VX415T',
'Virtex7 XC7VX485T','Virtex7 XC7VX550T','Virtex7 XC7VX690T','Virtex7 XC7VX980T','Virtex7 XC7VX1140T','Virtex7 XC7VH290T',
'Virtex7 XC7VH580T','Virtex7 XC7VH870T','Virtex6 XC6VLX75T','Virtex6 XC6VLX130T','Virtex6 XC6VLX195T','Virtex6 XC6VLX240T ',
'Virtex6 XC6VLX365T','Virtex6 XC6VLX550T','Virtex6 XC6VLX760','Virtex6 XC6VSX315T','Virtex6 XC6VSX475T','Virtex6 XC6VHX250T',
'Virtex6 XC6VHX255T','Virtex6 XC6VHX380T','Virtex6 XC6VHX565T','Virtex6Q XQ6VLX130T','Virtex6Q XQ6VLX240T','Virtex6Q XQ6VLX550T',
'Virtex6Q XQ6VSX315T','Virtex6Q XQ6VSX475T','Virtex5 XC5VLX30','Virtex5 XC5VLX50','Virtex5 XC5VLX85','Virtex5 XC5VLX110',
'Virtex5 XC5VLX155','Virtex5 XC5VLX220','Virtex5 XC5VLX330','Virtex5 XC5VLX20T','Virtex5 XC5VLX30T','Virtex5 XC5VLX50T',
'Virtex5 XC5VLX85T','Virtex5 XC5VLX110T','Virtex5 XC5VLX155T','Virtex5 XC5VLX220T','Virtex5 XC5VLX330T','Virtex5 XC5VSX35T',
'Virtex5 XC5VSX50T','Virtex5 XC5VSX95T','Virtex5 XC5VSX240T','Virtex5 XC5VFX30T','Virtex5 XC5VFX70T','Virtex5 XC5VFX100T',
'Virtex5 XC5VFX130T','Virtex5 XC5VFX200T','Virtex5Q XQ5VLX85','Virtex5Q XQ5VLX110','Virtex5Q XQ5VLX30T','Virtex5Q XQ5VLX110T',
'Virtex5Q XQ5VLX155T','Virtex5Q XQ5VLX220T','Virtex5Q XQ5VLX330T','Virtex5Q XQ5VSX50T','Virtex5Q XQ5VSX95T','Virtex5Q XQ5VSX240T',
'Virtex5Q XQ5VFX70T','Virtex5Q XQ5VFX100T','Virtex5Q XQ5VFX130T','Virtex5Q XQ5VFX200T','Virtex5QV XQR5VFX130','Virtex4 XC4VLX15',
'Virtex4 XC4VLX25','Virtex4 XC4VLX40','Virtex4 XC4VLX60','Virtex4 XC4VLX80','Virtex4 XC4VLX100','Virtex4 XC4VLX160',
'Virtex4 XC4VLX200','Virtex4 XC4VSX25','Virtex4 XC4VSX35','Virtex4 XC4VSX55','Virtex4 XC4VFX12','Virtex4 XC4VFX20',
'Virtex4 XC4VFX40','Virtex4 XC4VFX60','Virtex4 XC4VFX100','Virtex4 XC4VFX140','Virtex4Q XQ4VLX25','Virtex4Q XQ4VLX40',
'Virtex4Q XQ4VLX60','Virtex4Q XQ4VLX80','Virtex4Q XQ4VLX100','Virtex4Q XQ4VLX160','Virtex4Q XQ4VSX55','Virtex4Q XQ4VFX60',
'Virtex4Q XQ4VFX100','Virtex4QV XQR4VSX55','Virtex4QV XQR4VFX60','Virtex4QV XQR4VFX140','Virtex4QV XQR4VLX200','Spartan6 XC6SLX4',
'Spartan6 XC6SLX9','Spartan6 XC6SLX16','Spartan6 XC6SLX25','Spartan6 XC6SLX45','Spartan6 XC6SLX75','Spartan6 XC6SLX100',
'Spartan6 XC6SLX150','Spartan6 XC6SLX25T','Spartan6 XC6SLX45T','Spartan6 XC6SLX75T','Spartan6 XC6SLX100T','Spartan6 XC6SLX150T',
'Spartan6Q XQ6SLX75','Spartan6Q XQ6SLX150','Spartan6Q XQ6SLX75T','Spartan6Q XQ6SLX150T','Spartan3A_DSP XC3SD1800A',
'Spartan3A_DSP XC3SD3400A','Spartan3AN XC3S50AN','Spartan3AN XC3S200AN','Spartan3AN XC3S400AN','Spartan3AN XC3S700AN',
'Spartan3AN XC3S1400AN','Spartan3A XC3S50A','Spartan3A XC3S200A','Spartan3A XC3S400A','Spartan3A XC3S700A','Spartan3A XC3S1400A',
'Spartan3L XC3S1000L','Spartan3L XC3S1500L','Spartan3L XC3S4000L','Spartan3E XC3S100E','Spartan3E XC3S250E','Spartan3E XC3S500E',
'Spartan3E XC3S1200E','Spartan3E XC3S1600E','Spartan3 XC3S50','Spartan3 XC3S200','Spartan3 XC3S400','Spartan3 XC3S1000',
'Spartan3 XC3S1500','Spartan3 XC3S2000','Spartan3 XC3S4000','Spartan3 XC3S5000','CoolRunnerII XC2C32A','CoolRunnerII XC2C64A',
'CoolRunnerII XC2C128','CoolRunnerII XC2C256','CoolRunnerII XC2C384','CoolRunnerII XC2C512','XC9500XL XC9536XL','XC9500XL XC9572XL',
'XC9500XL XC95144XL','XC9500XL XC95288XL']
#dev_device = [x.split()[1] for x in dev_device]

dev_package=['BG256','CP132','CP56','CPG132','CPG196','CPG236','CS144','CS280',
'CS48','CS484','CSG144','CSG225','CSG324','CSG484','FBG484','FBG676','FBG900',
'FF1136','FF1136','FF1148','FF1152','FF1153','FF1154','FF1155','FF1156',
'FF1517','FF1738','FF1759','FF1760','FF1760','FF1923','FF1924','FF323','FF324',
'FF484','FF665','FF668','FF672','FF676','FF784','FFG1155','FFG1156','FFG1157',
'FFG1158','FFG1159','FFG1761','FFG1925','FFG1926','FFG1927','FFG1928','FFG1929',
'FFG1930','FFG1931','FFG1932','FFG484','FFG676','FFG784','FFG900','FG208',
'FG256','FG320','FG324','FG400','FG456','FG484','FG484','FG676','FG900',
'FGG484','FGG676','FGG784','FGG900','FT256','FTG256','PC44','PQ208','PQG208',
'QF32','QF48','RF1156','RF1759','RF784','SBG324','SF363','TQ100','TQ144',
'TQG100','TQG144','VQ100','VQ44','VQ64','VQG100']


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

# create a "src" folder and put in it two basic VHDL files as well as a
# constraints file. This is just to help beginners to get started with boot

def quick_start():
    call('clear'.split())

    content_fl1 = '''--- ##### file: counter_top.vhdl #####
-- This is the VHDL top-level design file. This file defines the top-level 
-- entity of your VHDL design.
-- library
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all; 
 
-- entity
entity counter_top is
port (
     cout    :out std_logic_vector (7 downto 0);
     up_down :in  std_logic;               -- up down control for counter
     clk     :in  std_logic;               -- Input clock
     reset   :in  std_logic);              -- Input reset
end entity;

-- architecture
architecture rtl of counter_top is
    signal count :std_logic_vector (7 downto 0);
    begin
        process (clk, reset) begin 
            if (reset = '1') then  
                count <= (others=>'0');
            elsif (rising_edge(clk)) then
                if (up_down = '1') then
                    count <= std_logic_vector(unsigned(count) + 1);
                else
                    count <= std_logic_vector(unsigned(count) - 1);
                end if;
            end if;
        end process;
        cout <= count;
end architecture;
'''

    content_fl2 = '''--- ##### file: counter_tb.vhdl #####
-- This is the test-bench file and is used to drive the simulation of 
-- your design. This file is not used during synthesis.
-- library
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

-- entity
entity counter_tb is
end entity;

-- architecture
architecture TB of counter_tb is
 
    component counter_top
    port( cout:     out std_logic_vector(7 downto 0);
          up_down:  in std_logic;
          reset:    in std_logic;
          clk:      in std_logic);
    end component;
 
    signal cout:    std_logic_vector(7 downto 0);
    signal up_down: std_logic; 
    signal reset:   std_logic; 
    signal clk:     std_logic; 
 
begin
 
    dut: counter_top port map (cout, up_down, reset, clk); 
 
    process
    begin
        clk <= '0';  
        wait for 10 ns;
        clk <= '1';
        wait for 10 ns;
    end process;

    process
    begin
        up_down <= '1';
        reset <= '1';
        wait for 10 ns;
        reset <= '0';
        wait for 500 ns;
 
        up_down <= '0';
        wait for 500 ns;
    end process;
end;
'''

    content_fl3 = '''--- ##### file: board.ucf #####
# simple example of a constraints file that you need when synthesize
# your design. This file is specific to your FPGA board.

net fpga_clk       loc = p43;
net sdram_clk      loc = p40;
net sdram_clk_fb   loc = p41;
net ras_n          loc = p59;
net cas_n          loc = p60;
net we_n           loc = p64;
net bs             loc = p53;
net a<0>           loc = p49;
net a<1>           loc = p48;
net a<2>           loc = p46;
'''

    print 'Building a "src" folder and a basic VHDL working environment.' 
    try:
        os.path.os.mkdir(os.path.join(os.getcwd(), 'src')) # make "src" dir
        open(os.path.join(os.getcwd(),'src','counter_top.vhdl'),'w').write(content_fl1)
        open(os.path.join(os.getcwd(),'src','counter_tb.vhdl'),'w').write(content_fl2)
        open(os.path.join(os.getcwd(),'src','board.ucf'),'w').write(content_fl3)            
    except:
        print 'Problems in writing. You might have permission problems or\n', \
              'the "src" folder already exists.\n'
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

# generate and save a Xilinx ISE xtclsh script
def gen_xil_syn_script(syn_out_dir, tld_file, vhdl_files, constraints_file,
                       dev_family,dev_device, dev_package, dev_speed):

    # formal vhdl file list
    vhdl_files = '[ list ../' + ' ../'.join(vhdl_files) + ' ]'

    # format constraints file list and take ONLY the first one
    if len(constraints_file) == 0:
        constraints_file = ''
    elif len(constraints_file)>0:
        constraints_file = constraints_file[0]
        constraints_file = os.path.basename(constraints_file) # strip whole path
        constraints_file = '../' + constraints_file
    content = '''#
# xil_syn_script.tcl
#
# script to synthesize your design using xtclsh from Xiling ISE
# usage: xtclsh build/xil_syn_script.tcl
#
# this file is automatically generated by "boot"
#
# to use this script you need Xilinx ISE 12.x or later

# output folder
set compile_directory   %s
# top-level desing file
set tld_file            %s
# input source files:
set vhdl_files          %s

# constraint file
set constraints_file    %s

# Xilinx CableServer host PC:
set cableserver_host {}

set proj $tld_file

puts "Running ISE xtclsh script: \\"xil_syn_script.tcl\\" automatically generated"

if { $cableserver_host == "" } {
  puts "Running with the board connected to the local machine.\\n"
} else {
  puts "Running with the board connected to $cableserver_host.\\n"
}

# Set compile directory
if {![file isdirectory $compile_directory]} {
  file mkdir $compile_directory
   }
cd $compile_directory


# Create a new project or open project
set proj_exists [file exists $proj.xise]

if {$proj_exists == 0} {
    puts "Creating a new Xilinx ISE project ..."
    project new $proj.xise

    # Project settings
    project set family  %s
    project set device  %s
    project set package %s
    project set speed   %s

    # Add source files to the project
    foreach filename $vhdl_files {
      xfile add $filename
    }
    xfile add $constraints_file

    # Make sure $source_directory is properly set
    if { ! [catch {set source_directory $source_directory}] } {
      project set "Macro Search Path" $source_directory -process Translate
    }

} else {

    puts "Opening existing Xilinx ISE project"

    # Open the existing project
    project open $proj.xise
}

# Implementation properties options
# MAP
#project set "Map Effort Level" Medium -process map
#project set "Perform Timing-Driven Packing and Placement" true -process map
#project set "Register Duplication" true -process map
#project set "Retiming" true -process map

# PAR
#project set "Place & Route Effort Level (Overall)" Standard
#project set "Extra Effort (Highest PAR level only)" Normal

# Implement Design
puts "Implement Design..."
# process run "Implement Design"
process run "Generate Programming File"
project close

# All done
puts "End of ISE Tcl script.\\n"

# Download .bit file into your FPGA/CPLD device using impact

# impact cannot be directly run via xtclsh, instead
# an impact script file will be created  and run
set impact_script_filename impact_script.scr
set bit_filename $tld_file.bit

if [catch {set f_id [open $impact_script_filename w]} msg] {
  puts "Can't create $impact_script_filename"
  puts $msg
  exit
}

# For Spartan3E starter kit
if { $cableserver_host == "" } {
        # Assume using locally connected board
        puts $f_id "setMode -bscan"
        puts $f_id "setCable -p usb21"

} else {
        # Assume using cableserver on cableserver_host
        puts $f_id "setMode -bscan"
        puts $f_id "setCable -p usb21 -server $cableserver_host"
}
puts $f_id "addDevice -position 1 -file $bit_filename"
puts $f_id "addDevice -p 2 -part xcf04s"
puts $f_id "addDevice -p 3 -part xc2c64a"
puts $f_id "readIdcode -p 1"
puts $f_id "program -p 1"
puts $f_id "quit"
close $f_id

#puts "\\n Switch on the Spartan3E board, connect the USB cable."
#puts -nonewline "  Press Enter when you are ready to download...\\a"
#flush stdout
#
# The "gets" command fails with the following message, if running within
# the ISE Project Navigator GUI.
#
#   channel "stdin" wasn't opened for reading
#
#if [catch {gets stdin ignore_me} msg] {
#  puts "\\n\\n *** $msg"
#  puts " *** Carrying on regardless ...\\n"
#  flush stdout
#}
# run impact script redirecting stdout
# set impact_p [open "|impact -batch $impact_script_filename" r]
# while {![eof $impact_p]} { gets $impact_p line ; puts $line }
# close $impact

# END
''' %('build', tld_file, vhdl_files, constraints_file, \
      dev_family, dev_device, dev_package, dev_speed)
    # NOTE: above we have used "build" directory and not syn_out_dir

    try:
        print 'Generating Xilinx ISE xtclsh script'
        if os.path.isdir(syn_out_dir):
            open(os.path.join(syn_out_dir,'xil_syn_script.tcl'),'w').write(content)
        else:
            print 'Problems in writing, you might have permission problems.'
    except:
        print 'Problems in writing, you might have permission problems.'
        return 1

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
    # this action is triggered with the ENTER key
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
    # is in focus and CTRL+D is pressed
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

        print 'Synthesis script about to ge generated.'
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
            if gen_xil_syn_script(syn_out_dir, tl, files, constraints_file, 
                                  fa, de, pa, sp):
                print 'Synthesis script generation process failed.'
                return 1
            print 'Xilinx synthesis script generated.'
            # update the synthesis command field
            self.tool_command_entry.set_text('xtclsh build/xil_syn_script.tcl')
        except:
            print 'Problems in saving the Xilinx synthesis script.'
            print 'Maybe you have rights permission problems.'
            return 1
        return 0







    # Start and stop the Synthesis of your vhdl design
    def syn_button_action(self, widget, action):

        # get information from Synthesis tab
        tl = self.dir_entry.get_text()
        syn_path = self.tool_path_entry.get_text()
        syn_cmd = self.tool_command_entry.get_text()
        wd = os.path.dirname(os.path.realpath(self.dir_entry.get_text()))

        # work in progress warming window
        #self.on_warn('Sorry mate, this feature is not implemented yet.')

        # execute stuff
        if action=='start':

            #save some parameters on local "~/.boot" file
            self.save_configuration_locally()
            
            # begin synthesis process unless it has been already started
            if self.syn_p!=None and self.syn_p.poll() ==None:
                print 'Synthesis process already running.'
                return 0
            print 'Starting synthesis process.'
            self.syn_textbuffer.set_text('Synthesis process output window.')
            self.syn_textbuffer.insert_at_cursor('\n') # this just add text

            # delete all ISE project inside "build"
            # this will guarantee that synthesis will start from the beginning
            all_unwanted_fls = glob.glob(os.path.join(wd,'build','*.xise'))
            for fl in all_unwanted_fls:
                os.remove(fl)

            # execute the "source" command (using ".") and also
            command = ['bash','-c',syn_path + '>>/dev/null; env']
            proc = Popen(command, stdout = PIPE)

            # import and apply the new environment values using "os.environ"
            for line in proc.stdout:
                (key, _, value) = line.partition("=")
                os.environ[key] = value
            proc.communicate()
            #pprint.pprint(dict(os.environ))

            # change directory and run synthesis script
            cmd = 'cd src/; '+ syn_cmd
            self.syn_p = Popen(cmd, shell=True, stdout=PIPE, stderr=STDOUT)

            # lets now redirect "self.syn_p" stdout to a GUI method using "gobject"
            gobject.io_add_watch(self.syn_p.stdout,
                                 gobject.IO_IN,
                                 self.write_to_syn_output)
            # done !

        # TODO this kill process does not seem to work
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

        print 'HHHHHHHHHHHHHH'
        return 0













    # this method will style each line that gets displayed
    # in the synthesis text output window
    def beautifier(self, widget, _in):
        position = self.syn_textbuffer.get_end_iter()

        # let's filter the content and apply the many styles
        if 'not found' in _in:
            self.syn_textbuffer.insert_with_tags( position, _in, self.red_tag) # red font type
        elif 'error' in _in or 'ERROR' in _in:
            self.syn_textbuffer.insert_with_tags( position, _in, self.red_tag, self.bold_tag) # red and bold font type
        elif 'warning' in _in or 'WARNING' in _in:
            self.syn_textbuffer.insert_with_tags( position, _in, self.orange_tag) # orange font type
        elif 'successful' in _in:
            self.syn_textbuffer.insert_with_tags( position, _in, self.green_tag) # green font type
        elif ('Summary' in _in) or ('Report' in _in):
            self.syn_textbuffer.insert_with_tags( position, _in, self.bold_tag) # bold font type
        else:
            self.syn_textbuffer.insert_with_tags( position, _in, self.gray_tag) # gray font type
        return _in

    # this method allows data in to get directed to the synthesis output window
    def write_to_syn_output(self, fd, condition):
        if condition == gobject.IO_IN:
            #char = fd.read(1) # read one byte at the time
            char = fd.readline()
            char = self.beautifier(self, char)
            #self.syn_textbuffer.insert_at_cursor(char)
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
        for x in dev_device:
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
        self.set_default_button_label.set_text('Done, you should now restart boot.')
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
            self.pr_pbar.set_text("you seem to be off line")
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

    # re-scroll the synthesis text output window so that
    # new text is always shown
    def syn_rescroll(self, widget):
        self.vadj.set_value(self.vadj.upper-self.vadj.page_size)
        self.syn_scroller.set_vadjustment(self.vadj)

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
        self.sim_opt_entry.set_text('--stop-time=200ns')
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
        tooltips.set_tip(self.dir_entry, 
        'Here you select the top-level design file.\n\n'+
        'ENTER:  create a new file.\n' +
        'CTRL-D: delete current file.\n')

        # let's trigger an action when the text changes
        self.dir_entry.connect("changed", self.dir_entry_changed)

        # let's trigger a "create file" action when the return key is pressed
        self.dir_entry.connect("activate", self.make_new_file)

        # let's trigger a "delete file" action when top-level design file entry
        # is in focus and ctrl+D is pressed
        self.dir_entry.connect('key-press-event', self.entry_keypress)

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
        tooltips.set_tip(self.top_level_label, 'This is your top-level design '+
                        'file. You can edit this in the Compile tab.')
        self.tool_path_entry = gtk.Entry() # synthesis tool path
        tooltips.set_tip(self.tool_path_entry, 'This is the path where the '+
                        'synthesis tools are installed.')
        self.tool_command_entry = gtk.Entry() # synthesis tool command
        tooltips.set_tip(self.tool_command_entry, 'This is the command to '+
                        'synthesis your design.')

        Hbox_syn1.pack_start(self.top_level_label, False, False, 3)
        Hbox_syn2.pack_start(gtk.Label('Synthesis tool path setting command: '), False, False,3)
        #self.tool_path_entry.set_width_chars(90)
        Hbox_syn2.pack_start(self.tool_path_entry, True, True, 3)
        Hbox_syn3.pack_start(gtk.Label('Synthesis command: '), False, False,3)
        Hbox_syn3.pack_start(self.tool_command_entry, True, True, 3)
        Hbox_syn5.pack_start(gtk.Label('Device type: '), False, False,3)

        # populate FPGA family, device and package fields
        self.ma = self.make_dropdown_menu(dev_manufacturer)
        self.fa = self.make_dropdown_menu(dev_family)
        self.de = self.make_dropdown_menu(dev_device)
        self.pa = self.make_dropdown_menu(dev_package)
        self.sp = self.make_dropdown_menu(dev_speed)
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
        self.syn_textbuffer.set_text('ready to go!') 

        # style the synthesis output text area
        syn_out.modify_font(pango.FontDescription('monospace 9'))

        #self.syn_textbuffer.set_use_markup(gtk.TRUE)
        #self.syn_textbuffer.set_markup('<span size="11000" foreground="black"> hi !</span>')

    
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
        start_syn_button = gtk.Button('Start Synthesis')
        stop_syn_button = gtk.Button('Stop Synthesis')
        gen_syn_script_button = gtk.Button('Generate Script')
        self.syn_p = None # this is the synthesize process handler
        start_syn_button.connect("clicked", self.syn_button_action, 'start')
        stop_syn_button.connect("clicked", self.syn_button_action, 'stop')
        gen_syn_script_button.connect("clicked", self.gen_syn_script_button_action,'gen_script')
        Hbox_syn4.pack_start(gen_syn_script_button, False, False, 3)
        Hbox_syn4.pack_start(start_syn_button, False, False, 3)
        Hbox_syn4.pack_start(stop_syn_button, False, False, 3)
        Vbox_syn1.pack_start(Hbox_syn4, False, False, 7)
        Vbox_syn1.pack_start(self.syn_scroller, True, True)

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
        set_default_button = gtk.Button('Set Default')
        self.set_default_button_label = gtk.Label('Reset boot to its default configuration.')
        pr_Hbox1 = gtk.HBox(False, 0)
        pr_Hbox2 = gtk.HBox(False, 0)
        pr_Hbox1.pack_start(check_updates_button, False, False, 7)
        pr_Hbox2.pack_start(set_default_button, False, False, 7)
        pr_Hbox2.pack_start(self.set_default_button_label, False, False, 2)
        self.pr_pbar = gtk.ProgressBar(adjustment=None) # progress bar for "Check for Updates"
        pr_Hbox1.pack_start(self.pr_pbar, False, False, 7)
        self.pr_pbar.set_size_request(400,-1)
        #self.pr_pbar.set_text("you seem to be offline")
        #self.pr_pbar.set_fraction(0.2) 
        pr_Vbox1 = gtk.VBox(False, 0)
        pr_Vbox1.pack_start(pr_Hbox1, False, False, 7)
        pr_Vbox1.pack_start(pr_Hbox2, False, False, 7)
        notebook.append_page(pr_Vbox1, gtk.Label('Preferences'))
        check_updates_button.connect("clicked", self.update_boot)
        set_default_button.connect("clicked", self.set_default_boot)
        tooltips.set_tip(check_updates_button, "Download a new version of boot")
        tooltips.set_tip(set_default_button, "Set boot to its default status")

        # define the beautifier styles
        self.blue_tag = self.syn_textbuffer.create_tag( "blue", foreground="#FFFF00", background="#0000FF")
        self.it_tag = self.syn_textbuffer.create_tag( "it", style=pango.STYLE_ITALIC)
        self.bold_tag = self.syn_textbuffer.create_tag( "bold", weight=pango.WEIGHT_BOLD)
        self.red_tag = self.syn_textbuffer.create_tag( "red", foreground="#FF0000")
        self.green_tag = self.syn_textbuffer.create_tag( "green", foreground="#21E01F")
        self.gray_tag = self.syn_textbuffer.create_tag( "gray", foreground="#5E5E5E")
        self.orange_tag = self.syn_textbuffer.create_tag( "orange", foreground="#FF8804")



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
        default_www = 'http://www.freerangefactory.org/site/pmwiki.php/Main/BootDoc'
        self.www_adr_bar.set_text(default_www)
        self.browser.open(default_www)

        ######## POPULATE SYNTHESIZE TAB ########

        # just copy content from the compile dir entry field
        self.top_level_label.set_text('Top-level design: ' + \
                                      self.dir_entry.get_text())

        # try to guess the Xilinx xtclsh synthesis tool path by checking
        # Xilinx ISE environment variables and generate a "source" command with "."
        try:
            answer = os.environ.get("XILINX_DIR")
            cmd = 'source ' + answer + '/settings64.sh'
            self.tool_path_entry.set_text(cmd)
            print 'Xilinx ISE software too detected at:', answer
        except:
            # set the kind of default Xilinx ISE path (maybe we could try to search for it)
            self.tool_path_entry.set_text('source /opt/Xilinx/13.2/ISE_DS/settings64.sh')

        # default xtclsh command
        self.tool_command_entry.set_text('Not set')

        # load data from a possible ~/.boot local file
        # NOTE: this will overwrite lots of GUI variables.
        self.load_local_configuration_file()

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

    parser.add_argument('-qs','--quick_start', required=False, dest='quick_start', 
                        action='store_const', const=True, default=False,
                        help='Build a quick and dirty VHDL working environment')

    args = parser.parse_args()

    # load stuff accordingly
    try:
        if args.build:
            build()
        elif args.quick_start:
            quick_start()
        else:
            # redirect standard output
            #sys.stdout = open('boot.log', 'w')
            #sys.stdout = open('/dev/null', 'w')
            main()
    except KeyboardInterrupt:
        print 'bye bye.'




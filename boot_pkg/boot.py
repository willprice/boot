#!/usr/bin/env python
'''
FILE: boot.py

application to compile, simulate and synthesize your VHDL code.
how to run: ./boot

Copyright (C) 2012 Fabrizio Tappero

Site:     http://www.freerangefactory.org
Author:   Fabrizio Tappero, fabrizio.tappero<at>gmail.com
License:  GNU General Public License
'''

import gtk, argparse
from multiprocessing import Process, Pipe

import gui 
import boot_process
from build import build_all
import quick_start

__author__ = 'Fabrizio Tappero'

# turn on the GUI
def gui_up():
    gtk.main()
    return 0

# this is boot main program
def boot():

    # create a pipe for communication between compilation & simulation process
    # an the boot GUI
    comm_i, comm_o = Pipe()

    # create and start process for compile and simulate
    compute_prc = Process(target=boot_process.comp_and_sim, args=(comm_o,))

    compute_prc.start()

    # make GUI object and start it.
    # the compute process and the communication pipe is passed to the GUI
    my_gui = gui.mk_gui()
    my_gui.add_conn(compute_prc, comm_i)
    gui_up()

    # terminate all processes
    compute_prc.terminate()
    compute_prc.join()
    return 0

# main
def main():

    # load parser for help options
    parser = argparse.ArgumentParser(
             description = 'Program to compile, simulate and synthesize '+\
                           'your VHDL code.',
             epilog = "Program made by: freerangefactory.org")

    parser.add_argument('-b','--build', required=False, dest='build', 
                        action = 'store_const', const = True, default = False,
                        help = 'Download and install necessary packages ' +\
                               '(Internet connection required).')

    parser.add_argument('-qs','--quick_start', required = False, 
                        dest = 'quick_start', action = 'store_const', 
                        const = True, default = False,
                        help = 'Build a simple VHDL project.')

    args = parser.parse_args()

    # load stuff accordingly
    try:
        if args.build:
            build_all()
        elif args.quick_start:
            quick_start.make_vhdl_counter_project('src')
        else:
            # redirect standard output
            #sys.stdout = open('boot.log', 'w')
            #sys.stdout = open('/dev/null', 'w')
            boot()
    except KeyboardInterrupt:
        print 'bye bye.'
    return 0

# to be executed when you call "./boot"
if __name__ == "__main__":
    main()



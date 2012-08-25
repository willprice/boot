#!/usr/bin/env python
#
# this file is part of the software tool BOOT
# URL: freerangefactory.org
# (C) 2012 Fabrizio Tappero
#
'''
FILE: boot.py

application to compile, simulate and synthesize your VHDL code.
how to run: ./boot

Copyright (C) 2012 Fabrizio Tappero

Site:     http://www.freerangefactory.org
Author:   Fabrizio Tappero, fabrizio.tappero<at>gmail.com
License:  GNU General Public License
'''

__author__ = 'Fabrizio Tappero'

# turn on the GUI
def gui_up():
    import gtk
    gtk.main()
    return 0

# this is boot main program
def boot():

    # import all necessary libraries. Importing libraries in this way allows,
    # for instance, the user to run "boot -b" without having to have all the
    # there libraries installedself.k
    from multiprocessing import Process, Pipe
    import gui 
    import boot_process
    
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

    import sys, argparse
    import quick_start, build

    # load parser for help options
    _parser = argparse.ArgumentParser(
             description = 'Program to compile, simulate and synthesize '+\
                           'your VHDL code.',
             epilog = "Program made by: freerangefactory.org")

    _parser.add_argument('-b','--build', required=False, dest='build', 
                        action = 'store_const', const = True, default = False,
                        help = 'Download and install necessary packages ' +\
                               '(Internet connection required).')

    _parser.add_argument('-qs','--quick_start', required = False, 
                        dest = 'quick_start', action = 'store_const', 
                        const = True, default = False,
                        help = 'Build a simple VHDL project.')

    _parser.add_argument('-l','--log', required = False, 
                        dest = 'log', action = 'store_const', 
                        const = True, default = False,
                        help = 'Start boot and log output into a local file.')

    _parser.add_argument('-v','--version', required = False, 
                        dest = 'ver', action = 'store_const', 
                        const = True, default = False,
                        help = 'Print the boot version number and exit.')

    args = _parser.parse_args()

    # load stuff accordingly
    try:
        if args.build:
            build.build_all()
        elif args.quick_start:
            # create a 'src' folder with a VHDL counter project in it
            quick_start.make_vhdl_counter_project('src')
        elif args.log:
            # redirect standard output to a local file
            sys.stdout = open('boot.log', 'w')
            boot()
        elif args.ver:
            import version
            print 'boot',version.boot_version
        else:
            #sys.stdout = open('/dev/null', 'w')     # redirect output to null
            boot()                                   # normal way to run "boot"
    except KeyboardInterrupt:
        print 'bye bye.'
    return 0

# to be executed when you call "./boot"
if __name__ == "__main__":
    main()



#
# this file is part of the software tool BOOT
# URL: freerangefactory.org
# (C) 2012 Fabrizio Tappero
#
import time, glob, os
from subprocess import Popen, PIPE, STDOUT

import directory

def comp_and_sim(conn):
    ''' Process to compile and simulate a vhdl design. This process is initiated 
        as soon as boot starts and it keeps running in background in a while 
        loop untill a trigger command is sent via its communication pipe.
    '''

    # some local variables (remember that we are in an independent process)
    COMPILATION_ERROR = False
    GTK_ALREADY_UP = False
    Compile = False
    Simulate = False

    while True:
        time.sleep(0.30)

        # load pipe info if there is any
        if conn.poll():
            [wd, tl_file, _SOCKET_ID, GHDL_SIM_OPT, Compile, Simulate] \
            = conn.recv()

        if Compile:
            # COMPILE
            Compile = False
            COMPILATION_ERROR = False

            # clean up GUI
            conn.send('CLEAR ALL\n')
            conn.send('Begin compiling\n')

            # before compile let's clean up the whole build folder
            # maybe for very big vhdl projects this is not a really good idea
            directory.dir_make_sure(wd, 'clean_all_files')

            # clean all GHDL files
            my_cmd = 'ghdl -clean --workdir=' + wd + '/build'
            p = Popen(my_cmd.split(' '), shell=False, stdout=PIPE, stderr=STDOUT)
            p.wait()
            print 'All GHDL files cleaned with process id:', p.pid

            # analyze ALL *.vhdl and *.vhd files
            all_vhdl_files = glob.glob(os.path.join(wd,'*.vhd')) + \
                             glob.glob(os.path.join(wd,'*.vhdl'))
            print 'Checking all VHDL files in:', wd
            for x in all_vhdl_files:
                conn.send('Checking: '+ x.replace(wd+'/',' ') + '\n')

            my_cmd = 'ghdl -a --workdir=' + wd + '/build ' + \
                     ' '.join(all_vhdl_files)
            p = Popen(my_cmd.split(' '), shell=False, stdout=PIPE,stderr=STDOUT)
            p.wait()
            print 'All vhdl files checked with process id:', p.pid

            for line in p.stdout.readlines():
                line = line.replace(wd+'/',' ')
                conn.send(line)

            # elaborate test bench file inside "build" directory
            # IMPORTANT: the top-level entity is the same
            #            as the tl_file name
            tl_entity = tl_file.split('.vhd')[0]# strip extension
            print 'Compiling top-level design file:', tl_entity
            my_cmd = 'ghdl -e --workdir=' + wd + '/build ' + tl_entity
            p = Popen(my_cmd.split(' '), shell=False, stdout=PIPE,stderr=STDOUT)
            p.wait()
            print 'All vhdl files compiled with process id:', p.pid
            
            for line in p.stdout.readlines():
                line = line.replace(wd+'/',' ')
                conn.send(line)
                # check for compilation errors
                if 'compilation error' in line:
                    COMPILATION_ERROR = True 
                else:
                    # no errors
                    COMPILATION_ERROR = False

            # move the executable tl_entity in folder "/build"
            if not COMPILATION_ERROR:
                print 'Moving simulation file:', tl_entity
                my_cmd = 'mv ' + tl_entity + ' ' + wd + '/build'
                p = Popen(my_cmd.split(' '), shell=False, stdout=PIPE,stderr=STDOUT)
                p.wait()
                print 'All build files moved with process id:', p.pid

            # done compiling
            conn.send('End compiling.\n')

        if Simulate and (not COMPILATION_ERROR):
            # SIMULATE
            Simulate = False

            # notify the beginning of a simulation
            conn.send('Begin simulation.\n')
            
            # generate simulation file
            tl_entity = tl_file.split('.vhd')[0]# strip file extension
            print 'Simulating top-level design:', tl_entity
            my_cmd = wd + '/build/' + tl_entity + ' ' + GHDL_SIM_OPT \
                     + ' --vcd='+wd+'/build/simul_output.vcd'
            p = Popen(my_cmd.split(' '), shell=False, stdout=PIPE,stderr=STDOUT)
            p.wait()
            print 'GHLD simulation files generated with process id:', p.pid

            for line in p.stdout.readlines():
                line = line.replace(wd+'/',' ')
                conn.send(line)

            # load the simulation output file with 
            if GTK_ALREADY_UP:
                # reload simulation file in the gtkwave GUI
                try:
                    _txt = 'Reloading GTKWAVE simulation file in process id:'
                    print _txt, p1.pid
                    cmd = 'gtkwave::reLoadFile\n'
                    p1.stdin.write(cmd)
                    p1.stdin.flush()
                except:
                    pass
            else:
                # start rtkwave GUI inside a terminal process
                cmd = 'gtkwave' + \
                      ' --rcfile='+ wd + '/build/gtkwaverc' + \
                      ' --xid=' + _SOCKET_ID + \
                      ' -W'
                p1 = Popen(cmd.split(), stdout=PIPE, stdin=PIPE, stderr=PIPE)
                print 'Started GHDL simulation process id:', p1.pid

                while not "Interpreter id is gtkwave" in p1.stdout.readline():
                    time.sleep(0.1)
                print "gtkwave is up."
                GTK_ALREADY_UP = True
                time.sleep(0.3)

                # load simulation file in the gtkwave GUI
                print 'Loading simulation interface with file:',tl_entity+'.vcd'
                cmd = 'gtkwave::loadFile "'+wd+'/build/simul_output.vcd"\n'
                p1.stdin.write(cmd)
                p1.stdin.flush()
                time.sleep(0.3)

            # done
            COMPILATION_ERROR = False
            conn.send('End processing\n')  

    return 0



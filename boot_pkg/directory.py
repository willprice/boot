#
# this file is part of the software tool BOOT
# URL: freerangefactory.org
# (C) 2012 Fabrizio Tappero
#
import glob, os, shutil

# global variables
before=[]

def src_dir_modified(wd):
    ''' src_dir_modified(wd)
        Check whether any VHDL file in folder "wd" has been modified.
    '''
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

def dir_make_sure(wd):
    ''' dir_make_sure(wd)
        Check that all directories and files inside "wd" are good.
        If the "build" directory exists, delete its content,
        if "build" directory does not exist, create it.
        Create  gtkwave conf. file and save in inside folder "build"
    '''
    # check that all directories and files exist
    if os.path.isdir(wd):
        print "Directory structure seems good."
        # make "build" directory inside wd
        if os.path.isdir(os.path.join(wd,'build'))==False:
            try:
                os.path.os.mkdir(os.path.join(wd,'build'))
                print '"build" directory created.'
            except:
                print 'Hum... you might not have writing permissions \
                       for the folder you are in... Exiting.'
                return False
        else:
            # delete all files and folders inside the "build" directory
            for root, dirs, files in os.walk(os.path.join(wd,'build')):
                for f in files:
                    os.unlink(os.path.join(root, f))
                for d in dirs:
                    shutil.rmtree(os.path.join(root, d))
            print 'All files and folders inside "build" were deleted.'

        # save gtkwave configuration file inside "build" folder
        print 'Creating gtkwave configuration file inside "build" folder'
        gtkwave_cnf_cont = '# gtkwave custom configuration file\n'+ \
                           '#\n# eliminate some keys\n#\n'+ \
                           'accel "/File/Read Sim Logfile" (null)\n'+ \
                           'accel "/File/Open New Window" (null)\n'+ \
                           'accel "/Edit/Toggle Trace Hier" (null)\n'+ \
                           'accel "/Edit/Toggle Group Open|Close" (null)\n'+ \
                           'accel "/Edit/Create Group" (null)\n'+ \
                           'accel "/Markers/Locking/Lock to Lesser Named Marker" (null)\n'+ \
                           'accel "/Markers/Locking/Lock to Greater Named Marker" (null)\n'+ \
                           'accel "/Markers/Locking/Unlock from Named Marker" (null)\n' + \
                           'accel "/File/Read Save File" (null)\n' + \
                           'accel "/Edit/Cut" (null)\n' + \
                           'accel "/File/Close" (null)\n' + \
                           'accel "/Edit/Paste" (null)\n' + \
                           'accel "/Edit/Copy" (null)\n' + \
                           'accel "/File/Open New Tab" (null)\n'
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



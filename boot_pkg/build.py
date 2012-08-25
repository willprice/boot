#
#
# this file is part of the software tool BOOT
# URL: freerangefactory.org
# (C) 2012 Fabrizio Tappero
#
import sys, os
from subprocess import call

try:
    from boot_pkg import nanorc
except:
    pass

def make_desktop_launcher():
    '''copy the boot launcher file from /usr/share/applications/ into 
       your ~/Desktop folder.
    '''
    try:
        cmd = 'sudo chmod +x /usr/share/applications/boot.desktop'
        call(cmd.split())

        cmd = 'cp /usr/share/applications/boot.desktop ' + \
               os.getenv("HOME") + '/Desktop/'
        call(cmd.split()) 
        
        # change owner and group of the desktop icon file 
        cmd = 'sudo chown '+ os.getlogin() +' '+ os.getenv("HOME") + \
              '/Desktop/boot.desktop'
        call(cmd.split())

        cmd = 'sudo chgrp '+ os.getlogin() +' '+ os.getenv("HOME") + \
              '/Desktop/boot.desktop'
        call(cmd.split()) 

        print 'Desktop launcher file created.'      
    except:
        print 'Problems in creating a desktop launcher file.'
    return 0


def build_all():
    '''Download and install everything that is needed for boot to function 
       properly.
    '''
    if 'linux' in sys.platform:                                       # LINUX OS
        call('clear')
        print 'Downloading and install necessary packages.'
        print 'You need to be connected to the Internet.\n'

        call('sudo apt-get install ghdl gtkwave'.split())
        make_desktop_launcher()

        # create a ~/.nanorc file to enable colors in nano.
        nanorc.make()

        # this is strictly necessary anymore. Pip is taking care of these 
        # dependencies. We will do it any way for the people who get "boot"
        # from source or from a source different then pip
        # see the file setup.py for more info.
        if True:
            #call('sudo apt-get update'.split()) # update apt-get database
            call('sudo apt-get install python-pip'.split())
            call('sudo apt-get install gtk2-engines-pixbuf'.split())
            call('sudo pip install argparse pygments mechanize'.split())

        # it is better to install pygtk from apt-get because pip seems to fail
        if True:
            call('sudo apt-get install python-gtk2 python-gobject'.split())


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
    print 'All done.\n'
    return 0  



import sys, os
from subprocess import call

try:
    from boot_pkg import nanorc
except:
    pass

# create a launcher file for boot which will go in the folder
# /usr/share/applications/
def make_desktop_launcher():
    try:
        cmd = 'cp /usr/share/applications/boot.desktop ' + os.getenv("HOME")+'/Desktop/'
        call(cmd.split()) 
        print 'Created desktop launcher file.'      
    except:
        print 'Problems in creating a desktop launcher file.'
    return 0

# Download and install everything that is needed for boot to function
def build_all():
    if 'linux' in sys.platform:                                       # LINUX OS
        call('clear')
        print 'Downloading and install necessary packages.'
        print 'You need to be connected to the Internet.\n'

        call('sudo apt-get install ghdl gtkwave'.split())
        make_desktop_launcher()

        # create a ~/.nanorc file to enable colors in nano.
        nanorc.make()

        # this is not necessary anymore. Pip is taking care of these dependencies
        # see the file setup.py for more info.
        if False:
            call('sudo apt-get update'.split()) # update apt-get database
            call('sudo apt-get install python-pip'.split())
            call('sudo apt-get install python-gtk2 python-gobject'.split())
            call('sudo apt-get install gtk2-engines-pixbuf'.split())
            call('sudo pip install argparse pygments'.split())

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



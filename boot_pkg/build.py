import sys
from subprocess import call

# Download and install everything that is needed for boot to function
def build_all():
    if 'linux' in sys.platform:                                       # LINUX OS
        call('clear')
        print 'Downloading and install necessary packages.'
        print 'You need to be connected to the Internet.\n'

        if False:
            call('sudo apt-get update'.split()) # update apt-get database
            call('sudo apt-get install python-pip'.split())
            call('sudo apt-get install python-gtk2 python-gobject'.split())
            call('sudo apt-get install gtk2-engines-pixbuf'.split())
            call('sudo pip install argparse pygments'.split())

        call('sudo apt-get install ghdl gtkwave'.split())

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

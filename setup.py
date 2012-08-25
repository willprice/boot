#!/usr/bin/env python
#
# this script will create a pip package or install "boot" in:
#   /usr/local/lib/pythonX.Y/dist-packages/boot_pkg
# plus icon, desktop launcher, and boot executable file
#
# see the end of this file for more help.
#
# for some help:
# http://docs.python.org/distutils/setupscript.html
#

from boot_pkg import version

from distutils.core import setup
#import py2exe
import sys


setup(
    name = 'boot',
    version = version.boot_version,
    description = 'VHDL simulator and synthesis tool',
    author = 'free range factory',
    author_email = 'contact@freerangefactory.org',
    url = 'http://www.freerangefactory.org',
    packages = ['boot_pkg'],
    package_dir={'boot_pkg': 'boot_pkg'},
    package_data={'boot_pkg': ['*.pyc']}, # '.py' are automatically added
    data_files=[('/usr/share/applications', ['boot_pkg/boot.desktop']), # dektop launcher
                ('/usr/share/icons', ['boot_pkg/icns/boot_icn.png'])],      # icon
    scripts = ['boot'], # the executable 'boot' will be put it '/usr/local/bin'
    install_requires=['Pygments', 'argparse','mechanize'],
    # remember that some boot depencencies will be installed with "sudo boot -b"
    license='GNU GPL License',
    long_description=open('README').read(),
    classifiers = [
                    'Programming Language :: Python',
                    'License :: OSI Approved :: GNU General Public License (GPL)',
                    'Operating System :: POSIX :: Linux',
                    'Environment :: X11 Applications :: GTK',
                    'Intended Audience :: Developers',
                    'Topic :: Desktop Environment',
                    'Natural Language :: English']
    )
#
# to create a pip distribiution file run:
#       python setup.py sdist --formats=zip
#
# to create a registration profile run:
#       python setup.py register
#
# the pip distribiution file can be manually uploaded on the
# Python cheese factory website: http://pypi.python.org/pypi
#
# to install locally run: 
#       sudo python setup.py install
#
# Installed files:
# /usr/local/bin/boot
# /usr/share/icons/boot.png
# /usr/share/applications/boot.desktop
# /usr/local/lib/python2.7/dist-packages/boot_pkg/*
# /usr/local/lib/python2.7/dist-packages/boot-0.19-py2.7.egg-info




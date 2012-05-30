#!/usr/bin/env python
# this script will create a pip package or install boot in:
#   /usr/local/lib/pythonX.Y/dist-packages/boot_pkg
# plus icon, desktop launcher, and boot executable
#
# for help:
# http://docs.python.org/distutils/setupscript.html

from distutils.core import setup
import sys

setup(
    name = 'boot',
    version = '0.19',
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
# to install locally run: 
#       sudo python setup.py install
#
# Installed files:
# /usr/local/bin/boot
# /usr/share/icons/boot.png
# /usr/share/applications/boot.desktop
# /usr/local/lib/python2.7/dist-packages/boot_pkg/*
# /usr/local/lib/python2.7/dist-packages/boot-0.19-py2.7.egg-info




#!/usr/bin/env python
# for help:
# http://docs.python.org/distutils/setupscript.html

from distutils.core import setup

setup(
    name = 'boot',
    version = '0.19',
    description = 'VHDL simulator and synthesis tool',
    author = 'free range factory',
    author_email = 'contact@freerangefactory.org',
    url = 'http://www.freerangefactory.org',
    packages = ['boot_pkg'],
    package_dir={'boot_pkg': 'boot_pkg'},
    package_data={'boot_pkg': ['icns/*.png']},
    scripts = ['boot'],
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
# to create a tar.bal run:
#       python setup.py sdist
#
# to upload your app ot the PyPI server (you need an account) run :
#       python setup.py sdist upload
#



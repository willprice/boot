# python libraries
import os, time, sys
import pygtk, gtk, gobject, pango, glob, argparse, fcntl
import ConfigParser, webkit, httplib, pprint, shutil
from gtk import gdk
pygtk.require('2.0')

from subprocess import call, Popen, PIPE, STDOUT
from multiprocessing import Process, Pipe

# local libraries
#from boot_io import *
import importlib
mods= [name.split(".py")[0] for name in os.listdir('./') if name.endswith(".py")]
for mod in mods:
    mod = importlib.import_module(mod)



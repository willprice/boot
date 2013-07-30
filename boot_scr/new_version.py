#
# this file is part of the software tool BOOT
# URL: freerangefactory.org
# (C) 2013 Fabrizio Tappero
#
import urllib2
import version as v

def check_for_new_version():
    '''Check for new versions of boot from freerangefactory.org'''
    try:
        fl = urllib2.urlopen("http://www.freerangefactory.org/dl/boot_last.txt")
        new_v = fl.read()
        if float(new_v) > v.boot_version:
            # new version available
            return True, "Boot version " + new_v + " available\n" +\
                         "Download it from: freerangefactory.org/sw" 
        else:
            return False, "No new version available."
    except:
        return False, "Server connection seems down."



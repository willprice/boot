#!/usr/bin/env python
#-*- coding:utf-8 -*-

import sys,os
sys.path.insert(0,os.path.abspath(__file__+"/../../boot_pkg"))

from quick_start import *

if __name__ == '__main__':

    import os
    _dir = os.path.join(os.getcwd(),'src')
    print _dir
    quick_start(_dir)



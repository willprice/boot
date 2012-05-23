#!/usr/bin/env python
#-*- coding:utf-8 -*-

import sys,os
sys.path.insert(0,os.path.abspath(__file__+"/../../boot_pkg"))

from editor import *

if __name__ == '__main__':

    _fl = os.path.join(os.getcwd(),'editor_test.py')
    text_editor(_fl).start()

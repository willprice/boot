#!/usr/bin/env python
#-*- coding:utf-8 -*-

import sys,os
sys.path.insert(0,os.path.abspath(__file__+"/../../boot_pkg"))

import editor

if __name__ == '__main__':

    _fl = os.path.join(os.getcwd(),'test_editor.py')
    editor.text_editor(_fl).start()

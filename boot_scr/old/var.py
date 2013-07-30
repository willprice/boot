#!/usr/bin/env python
#-*- coding:utf-8 -*-

from subprocess import Popen, PIPE, STDOUT

if __name__ == '__main__':
    cmd = 'source ./test.sh && echo $MY_VAR'
    p = Popen(cmd, shell=True, stdout=PIPE, stderr=STDOUT)
    p.wait()
    for line in p.stdout.readlines():
        print line





#!/usr/bin/env python2.6


import subprocess
import sys
import time

children = []
#Step 1: Launch all the children asynchronously
for i in range(10):
    #For testing, launch a subshell that will sleep various times
    popen = subprocess.Popen(["/bin/sh", "-c", "sleep %s" % (i + 8)])
    children.append(popen)
    print "launched subprocess PID %s" % popen.pid

#reverse the list just to prove we wait on children in the order they finish,
#not necessarily the order they start
children.reverse()
#Step 2: loop until all children are terminated
while children:
    #Step 3: poll all active children in order
    children[:] = [child for child in children if child.poll() is None]
    print "Still running: %s" % [popen.pid for popen in children]
    time.sleep(1)

print "All children terminated"


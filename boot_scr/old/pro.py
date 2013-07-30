#!/usr/bin/env python


import pprint, os
from subprocess import Popen, PIPE


command = ['bash','-c','source /opt/Xilinx/13.2/ISE_DS/settings64.sh>>/dev/null; env']
proc = Popen(command, stdout = PIPE)

for line in proc.stdout:
  (key, _, value) = line.partition("=")
  os.environ[key] = value
proc.communicate()
pprint.pprint(dict(os.environ))


#cmd = Popen("which xtclsh", stdout=PIPE, shell=True)
#data = cmd.communicate()[0]
#print data



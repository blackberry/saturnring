#!/usr/bin/python
import sys
import subprocess
import re
bashCommand = "sudo scstadmin -list_sessions"
process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
output = process.communicate()[0]
outlines = output.split('\n')
wkb=0
rkb=0
for aLine in outlines:
    if "Target: " in aLine:
        wkb=0
        rkb=0
        target = aLine.split('iscsi/')[1]
    if "write_io_count_kb" in aLine:
        wkb = re.findall('\d+',aLine)[0]
        print target,
        print rkb,
        print wkb
    if "read_io_count_kb" in aLine:
        rkb = re.findall('\d+',aLine)[0]




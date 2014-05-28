#!/usr/bin/python
#Copyright 2014 Blackberry Limited
#
#Licensed under the Apache License, Version 2.0 (the "License");
#you may not use this file except in compliance with the License.
#You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#Unless required by applicable law or agreed to in writing, software
#distributed under the License is distributed on an "AS IS" BASIS,
#WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#See the License for the specific language governing permissions and
#limitations under the License.


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
    if "(no sessions)" in aLine:
        print target,
        print "no sessions"



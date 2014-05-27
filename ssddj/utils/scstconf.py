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
def ParseSCSTConf(fileName):
    fH = open(fileName,"r")
    diskDic = {}
    targetDic = {}
    curDev = ""
    curTar = ""
    for aLine in fH:
        if "DEVICE " in aLine:
            curDev = aLine.split(" ")[1].rstrip()
            diskDic[curDev] ="NO_FILENAME"
            continue
        if "filename" in aLine:
            diskDic[curDev]=aLine.split(" ")[1].split("/")[-1].rstrip()
            curDev = "None"
        if "TARGET " in aLine:
            curTar = aLine.split(" ")[1].rstrip()
            targetDic[curTar]=["NO_DEVICE"]
        if "LUN " in aLine:
            if "NO_DEVICE" in targetDic[curTar]:
                targetDic[curTar]=[]
            targetDic[curTar].append(aLine.split(" ")[2].rstrip())
    fH.close()
    return (diskDic,targetDic)

if __name__=="__main__":
    if len(sys.argv) == 2:
        (diskDic,targetDic) = ParseSCSTConf(sys.argv[1])
    else:
        (diskDic,targetDic) = ParseSCSTConf("testscst.conf")
    import pprint
    pprint.pprint(diskDic)
    pprint.pprint(targetDic)

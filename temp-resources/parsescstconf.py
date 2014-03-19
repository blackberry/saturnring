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
            diskDic[curDev]=aLine.split(" ")[1].rstrip()
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
    (diskDic,targetDic) = ParseSCSTConf("scst.conf")
    import pprint
    pprint.pprint(diskDic)
    pprint.pprint(targetDic)

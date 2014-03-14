import pysftp #remember to use at least 0.2.2 - the pip install doesnt give you that version.
import sqlite3
import os
userName='vagrant'
keyFile='../config/saturnserver'
remoteinstallLoc='/home/vagrant/saturn/'
localbashscripts='./bashscripts/'

class PollServer():
    def __init__(self,serverIP):
        self.serverIP = serverIP
        self.InstallScripts()

    def InstallScripts(self):
        srv = pysftp.Connection(self.serverIP,userName,keyFile)
        srv.execute ('mkdir -p '+remoteinstallLoc+'saturn-bashscripts/')
        srv.chdir(remoteinstallLoc+'saturn-bashscripts/')
        locallist=os.listdir(localbashscripts)
        for localfile in locallist:
            srv.put(localbashscripts+localfile)
            srv.execute("chmod 777 "+remoteinstallLoc+'saturn-bashscripts/'+localfile)
        srv.close()

    def Exec(self,command):
        srv = pysftp.Connection(self.serverIP,userName,keyFile)
        rtncmd=srv.execute(command)
        srv.close()
        return rtncmd

    def ParseLVM(self,strList,delimitStr,paraList):
        rtnList =[]
        valueDict={}
        for aLine in strList:
            if (delimitStr in aLine):
                if len(valueDict) == len(paraList):
                    rtnList.append(valueDict)
                    valueDict = {}
                continue
            else:
                for anItem in paraList:
                    if anItem in aLine:
                        valueDict[anItem] = aLine.split(anItem)[1].strip()
                        continue
        if len(valueDict) == len(paraList):
             rtnList.append(valueDict)
        return rtnList 

    def GetLV(self, vgname='stripedvg'):
        lvStrList = self.Exec(" ".join(['sudo','lvdisplay',vgname]))
        delimitStr = '--- Logical volume ---'
        paraList=['LV Name','LV UUID','LV Size']
        lvs = self.ParseLVM(lvStrList,delimitStr,paraList)
        print lvs

    def GetVG(self,vgname='stripedvg'):
        vgStrList = self.Exec(" ".join(['sudo','vgdisplay',vgname]))
        delimitStr = '--- Volume group ---'
        paraList=['VG Size','PE Size','Total PE','Alloc PE / Size', 'Free  PE / Size', 'VG UUID']
        vgs = self.ParseLVM(vgStrList,delimitStr,paraList)
        print vgs


#Unit test
if __name__=="__main__":
    conn = sqlite3.connect('../db.sqlite3')
    cur = conn.cursor()
    cur.execute('SELECT * from ssdfrontend_storagehost')
    pollserver = PollServer(cur.fetchone()[2])
    pollserver.GetVG()
    #for aLine in pollserver.GetLV():
    #    print aLine
    #for aline in pollserver.Exec("".join(['sudo',' ',remoteinstallLoc,'saturn-bashscripts/','createlun.sh',' ','0.05'])):
    #    print aline



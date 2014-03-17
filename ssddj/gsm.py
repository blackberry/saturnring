import pysftp #remember to use at least 0.2.2 - the pip install doesnt give you that version.
import os
#from django.core.management import setup_environ
#from ssddj import settings
#setup_environ(settings)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ssddj.settings")

from django.core.management import execute_from_command_line

from ssdfrontend.models import VG
from ssdfrontend.models import StorageHost
from ssdfrontend.models import LV

userName='vagrant'
keyFile='./config/saturnserver'
remoteinstallLoc='/home/vagrant/saturn/'
localbashscripts='./bashscripts/'

class PollServer():
    def __init__(self,serverIP):
        self.serverIP = serverIP
        self.InstallScripts()
        #self.conn = sqlite3.connect('../db.sqlite3')
        #self.cur = self.conn.cursor()

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
                        if '%' in valueDict[anItem]:
                            valueDict[anItem] = float(valueDict[anItem][:-2])
                            continue
                        if '/' in valueDict[anItem]:
                            valueDict[anItem] = valueDict[anItem].split('/')[0]
                        if 'GiB' in valueDict[anItem]:
                            valueDict[anItem] = float(valueDict[anItem].split('GiB')[0])*1
                            continue
                        if 'MiB' in valueDict[anItem]:
                            valueDict[anItem] = float(valueDict[anItem].split('MiB')[0])*0.001
                            continue
                        continue
        if len(valueDict) == len(paraList):
             rtnList.append(valueDict)
        return rtnList 

    def GetLV(self, vgname='storevg'):
        lvStrList = self.Exec(" ".join(['sudo','lvdisplay',vgname]))
        delimitStr = '--- Logical volume ---'
        paraList=['LV Name','LV UUID','LV Size','Mapped size',]
        lvs = self.ParseLVM(lvStrList,delimitStr,paraList)
        print lvs

                
    def GetVG(self,vgname='storevg'):
        vgStrList = self.Exec(" ".join(['sudo','vgdisplay',vgname]))
        delimitStr = '--- Volume group ---'
        paraList=['VG Size','PE Size','Total PE', 'Free  PE / Size', 'VG UUID']
        vgs = self.ParseLVM(vgStrList,delimitStr,paraList)
        print vgs
        #hostid=self.cur.execute("""SELECT id FROM ssdfrontend_storagehost WHERE ipaddress=?""",(self.serverIP,)).fetchone()[0]
        hostid=StorageHost.objects.get(ipaddress=self.serverIP)
        #print hostid
        #snippet = Snippet(code='foo = "bar"\n')
        myvg = VG(vghost=hostid,vgsize=vgs[0]['VG Size'],
                vguuid=vgs[0]['VG UUID'],vgpesize=vgs[0]['PE Size'],
                vgtotalpe=vgs[0]['Total PE'],
                vgfreepe=vgs[0]['Free  PE / Size'])
        myvg.save()#force_update=True)

        #self.cur.execute("""INSERT OR REPLACE INTO ssdfrontend_vg (
        #vghost_id,vgsize,vguuid,vgpesize,vgtotalpe,vgfreepe) 
        #VALUES (?,?,?,?,?,?);""",(hostid,vgs[0]['VG Size'],vgs[0]['VG UUID'],
        #vgs[0]['PE Size'],vgs[0]['Total PE'],vgs[0]['Free  PE / Size']))
        #self.conn.commit()
        


#Unit test
if __name__=="__main__":
    pollserver = PollServer('192.168.61.20')
    pollserver.GetVG()
    pollserver.GetLV()
    #for aLine in pollserver.GetLV():
    #    print aLine
    #for aline in pollserver.Exec("".join(['sudo',' ',remoteinstallLoc,'saturn-bashscripts/','createlun.sh',' ','0.05'])):
    #    print aline



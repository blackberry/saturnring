import pysftp #remember to use at least 0.2.2 - the pip install doesnt give you that version.
import os
#from django.core.management import setup_environ
#from ssddj import settings
#setup_environ(settings)
#os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ssddj.settings")


from django.core.management import execute_from_command_line

from ssdfrontend.models import VG
from ssdfrontend.models import StorageHost
from ssdfrontend.models import LV
import logging
import utils.scstconf

userName='vagrant'
keyFile='./config/saturnserver'
remoteinstallLoc='/home/vagrant/saturn/'
localbashscripts='./globalstatemanager/bashscripts/'
logger = logging.getLogger(__name__)
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
        logger.info("Installed scripts")

    def Exec(self,command):
        srv = pysftp.Connection(self.serverIP,userName,keyFile)
        rtncmd=srv.execute(command)
        srv.close()
        return rtncmd

    def ParseLVM(self,strList,delimitStr,paraList):
        rtnDict ={}
        valueDict={}
        for aLine in strList:
            if (delimitStr in aLine):
                if len(valueDict) == len(paraList):
                    rtnDict[valueDict[paraList[0]]]=valueDict
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
             rtnDict[valueDict[paraList[0]]] = valueDict
        return rtnDict 

    def GetTargets(self):
        self.Exec(" ".join(['sudo', 'scstadmin','-w /etc/scst.conf']))
        srv = pysftp.Connection(self.serverIP,userName,keyFile)
        srv.get('/etc/scst.conf','config/'+self.serverIP+'.scst.conf')
        
    def GetLVs(self, vgname='storevg'):
        lvStrList = self.Exec(" ".join(['sudo','lvdisplay',vgname]))
        delimitStr = '--- Logical volume ---'
        paraList=['LV Name','LV UUID','LV Size','Mapped size']
        lvs = self.ParseLVM(lvStrList,delimitStr,paraList)
        return lvs
#        logger.info('Read LV '+str(lvs))
        #TODO - insert into the DB
                
    def GetVG(self,vgname='storevg'): #Unit test this again
        vgStrList = self.Exec(" ".join(['sudo','vgdisplay',vgname]))
        delimitStr = '--- Volume group ---'
        paraList=['VG Size','PE Size','Total PE', 'Free  PE / Size', 'VG UUID']
        vgs = self.ParseLVM(vgStrList,delimitStr,paraList)
        hostid=StorageHost.objects.get(ipaddress=self.serverIP)
        myvg = VG(vghost=hostid,vgsize=vgs[vgname]['VG Size'],
                vguuid=vgs[vgname]['VG UUID'],vgpesize=vgs[vgname]['PE Size'],
                vgtotalpe=vgs[vgname]['Total PE'],
                vgfreepe=vgs[vgname]['Free  PE / Size'])
        myvg.save()#force_update=True)
        logger.info('Read VG '+vgs)

    
    def CreateTarget(self,iqnTarget,sizeinGB):
        logger.info("Trying to create target %s of capacity %s GB" %(iqnTarget,str(sizeinGB)))
        srv = pysftp.Connection(self.serverIP,userName,keyFile)
        cmdStr = 'sudo /bin/bash '+remoteinstallLoc+'saturn-bashscripts/createtarget.sh' +' '+ str(sizeinGB)+' '+ iqnTarget
        exStr = srv.execute(cmdStr)
        logger.info("Execution report for %s:  %s" %(cmdStr,exStr))
        srv.close()
        if "SUCCESS" in str(exStr):
            logger.info("Returning successful createtarget run")
            return 1
        else:
            logger.info("Returning failed createtarget run")
            return 0



#Unit test
if __name__=="__main__":
    pollserver = PollServer('192.168.61.20')
    pollserver.GetVG()
    pollserver.GetLV()
    #for aLine in pollserver.GetLV():
    #    print aLine
    #for aline in pollserver.Exec("".join(['sudo',' ',remoteinstallLoc,'saturn-bashscripts/','createlun.sh',' ','0.05'])):
    #    print aline



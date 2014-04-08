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
from ssdfrontend.models import Target
import logging
from redisq import SchedulerQ
import utils.scstconf
logger = logging.getLogger(__name__)

class PollServer():
    def __init__(self,serverDNS):
        logger.info(" Scanning server %s" %(serverDNS,))
        self.userName='local'
        self.keyFile='./config/saturnserver'
        self.remoteinstallLoc='/home/local/saturn/'
        self.localbashscripts='./globalstatemanager/bashscripts/'

        self.serverDNS = str(serverDNS)
        #self.InstallScripts()

    def InstallScripts(self):
        srv = pysftp.Connection(self.serverDNS,self.userName,self.keyFile)
        srv.execute ('mkdir -p '+self.remoteinstallLoc+'saturn-bashscripts/')
        srv.chdir(self.remoteinstallLoc+'saturn-bashscripts/')
        locallist=os.listdir(self.localbashscripts)
        for localfile in locallist:
            srv.put(self.localbashscripts+localfile)
            srv.execute("chmod 777 "+self.remoteinstallLoc+'saturn-bashscripts/'+localfile)
        srv.close()
        logger.info("Installed scripts")

    def Exec(self,command):
        srv = pysftp.Connection(self.serverDNS,self.userName,self.keyFile)
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
        #self.Exec(" ".join(['sudo', 'scstadmin','-w /etc/scst.conf']))
        #srv = pysftp.Connection(self.serverDNS,userName,keyFile)
        #srv.get('/etc/scst.conf','config/'+self.serverDNS+'.scst.conf')
        return 0


    def UpdateLVs(self,vg):
        p = PollServer(vg.vghost)
        lvdict = p.GetLVs("storevg")
        lvs = LV.objects.all()
        for eachLV in lvs:
	    if eachLV.lvname in lvdict:
            	eachLV.lvsize=lvdict[eachLV.lvname]['LV Size']
            	eachLV.lvthinmapped=lvdict[eachLV.lvname]['Mapped size']
            	eachLV.save(update_fields=['lvsize','lvthinmapped'])
    
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
        paraList=['VG Name','VG Size','PE Size','Total PE', 'Free  PE / Size', 'VG UUID']
        vgs = self.ParseLVM(vgStrList,delimitStr,paraList)
        try:
            cmdStr = self.Exec(" ".join(['sudo',self.remoteinstallLoc+'saturn-bashscripts/thinlvstats.sh']))
            
            logger.info(self.serverDNS+": "+" ".join(['sudo','/bin/bash',self.remoteinstallLoc+'saturn-bashscripts/thinlvstats.sh'])+': LVS returned '+str(cmdStr))
            thinusedpercent = float(cmdStr[0].rstrip())
            thintotalGB = float(cmdStr[1].rstrip())
            maxthinavl = thintotalGB*(100-thinusedpercent)/100
        except:
            logger.warn("Unable to run LVScan on "+self.serverDNS)
            return -1
        logger.info(vgs)
        existingvgs = VG.objects.filter(vguuid=vgs[vgname]['VG UUID'])
        if len(existingvgs)==1:
            existingvg = existingvgs[0]
            existingvg.thinusedpercent=thinusedpercent
            existingvg.thintotalGB=thintotalGB
            existingvg.maxthinavlGB=maxthinavl
            existingvg.vgsize = vgs[vgname]['VG Size']
            existingvg.save(update_fields=['thinusedpercent','thintotalGB','maxthinavlGB','vgsize'])
        else:
            myvg = VG(vghost=StorageHost.objects.get(dnsname=self.serverDNS),vgsize=vgs[vgname]['VG Size'],
                    vguuid=vgs[vgname]['VG UUID'],vgpesize=vgs[vgname]['PE Size'],
                    vgtotalpe=vgs[vgname]['Total PE'],
                    vgfreepe=vgs[vgname]['Free  PE / Size'],
                    thinusedpercent=thinusedpercent,
                    thintotalGB=thintotalGB,maxthinavlGB=maxthinavl)
            myvg.save()#force_update=True)
        return vgs[vgname]['VG UUID']

    
   #     logger.info("Trying to create target %s of capacity %s GB" %(iqnTarget,str(sizeinGB)))
    def CreateTarget(self,iqnTarget,iqnInit,sizeinGB,storageip1,storageip2):
        srv = pysftp.Connection(self.serverDNS,self.userName,self.keyFile) 
        cmdStr = " ".join(['sudo','/bin/bash',self.remoteinstallLoc+'saturn-bashscripts/createtarget.sh',str(sizeinGB),iqnTarget,storageip1,storageip2,iqnInit])
        exStr = srv.execute(cmdStr)
        srv.get('/etc/scst.conf','config/'+self.serverDNS+'.scst.conf')
        logger.info("Execution report for %s:  %s" %(cmdStr,"\t".join(exStr)))
        srv.close()
        if "SUCCESS" in str(exStr):
            logger.info("Returning successful createtarget run")

#            self.GetVG() #Rescan VG to update
            return 1
        else:
            logger.info("Returning failed createtarget run")
            return 0
#Unit test
    def GetTargetsState(self):
        cmdStr = " ".join(["sudo", "/usr/bin/python",self.remoteinstallLoc+'saturn-bashscripts/parsetarget.py'])
        exStr = self.Exec(cmdStr)
        alltars = Target.objects.all()
        for eachLine in exStr:
            logger.info(eachLine)
            iqntar=eachLine.split()[0]
            tar = alltars.filter(iqntar=iqntar)
            if len(tar):
                tar = tar[0]
                if "no session" in eachLine:
                    tar.sessionup=False
                    tar.rkbpm = 0
                    tar.wkbpm = 0
                else:
                    tar.sessionup=True
                    rkb = long(eachLine.split()[1])
                    logger.info("parsed rkb ="+str(rkb))
                    logger.info("tar.rkb = "+str(tar.rkb))
                    tar.rkbpm = long(rkb-tar.rkb)
                    tar.rkb=rkb
                    wkb = long(eachLine.split()[2])
                    logger.info("parsed wkb ="+str(wkb))
                    logger.info("tar.wkb = "+str(tar.wkb))
                    wpm = long(wkb-tar.wkb)
                    logger.info("computed wpm = "+str(wpm))
                    tar.wkbpm = wpm
                    tar.wkb=wkb
                tar.save()

    def DeleteTarget(self,iqntar):
        self.GetTargetsState()
        try:
            tar = Target.objects.get(iqntar=iqntar)
        except:
            logger.warn("Could not find deletion target in DB, exiting. "+iqntar)
            return -1
        if not tar.sessionup:
            cmdStr = " ".join(["sudo", self.remoteinstallLoc+'saturn-bashscripts/removetarget.sh',iqntar])
            exStr = self.Exec(cmdStr)
            success1 = False
            success2 = False
            for eachLine in exStr:
                logger.info(eachLine)
                if "Removing virtual target '"+iqntar+"' from driver 'iscsi': done" in eachLine:
                    success1=True
                if "successfully removed" in eachLine:
                    success2=True
            if success1==True and success2==True:
                logger.debug("successfully removed target: "+iqntar)
                return 1
            else:
                return -1
        return -1



        


if __name__=="__main__":
    pollserver = PollServer('saturnserver0.store.altus.bblabs')
    cmdStr=pollserver.Exec("sudo /home/local/saturn/saturn-bashscripts/thinlvstats.sh")
    print cmdStr
#    pollserver.GetLV()
    #for aLine in pollserver.GetLV():
    #    print aLine
    #for aline in pollserver.Exec("".join(['sudo',' ',self.remoteinstallLoc,'saturn-bashscripts/','createlun.sh',' ','0.05'])):
    #    print aline



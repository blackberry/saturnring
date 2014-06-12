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

import pysftp #remember to use at least 0.2.2 - the pip install doesnt give you that version.
import os
from os import listdir
from os.path import isfile, join
import ConfigParser
from django.core.management import execute_from_command_line
from ssdfrontend.models import VG
from ssdfrontend.models import StorageHost
from ssdfrontend.models import LV
from ssdfrontend.models import Target
import logging
import utils.scstconf
from django.db.models import Sum
import subprocess
from dulwich.repo import Repo
import sys
import traceback
reload (sys)
sys.setdefaultencoding("utf-8")
logger = logging.getLogger(__name__)
class PollServer():
    def __init__(self,serverDNS):
        self.serverDNS = str(serverDNS)
        # Read configuration
        config = ConfigParser.RawConfigParser()
#        config.read('/home/vagrant/saturnring/ssddj/saturn.ini')
        BASE_DIR = os.path.dirname(os.path.dirname(__file__))
        print str(BASE_DIR)
        config.read(os.path.join(BASE_DIR,'saturn.ini'))
        self.userName=config.get('saturnnode','user')
        self.keyFile=os.path.join(BASE_DIR,config.get('saturnring','privatekeyfile'))
        self.rembashpath=config.get('saturnnode','bashpath')
        self.rempypath=config.get('saturnnode','pythonpath')
        self.vg=config.get('saturnnode','volgroup')
        self.iscsiconfdir=os.path.join(BASE_DIR,config.get('saturnring','iscsiconfigdir'))
        self.remoteinstallLoc=config.get('saturnnode','install_location')
        self.localbashscripts=os.path.join(BASE_DIR,config.get('saturnring','bashscripts'))

    # Copy over scripts from the saturnring server to the iscsi server
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

    # Helper function for executing a remote command over an SSH tunnel
    def Exec(self,command):
        srv = pysftp.Connection(self.serverDNS,self.userName,self.keyFile)
        rtncmd=srv.execute(command)
        srv.close()
        return rtncmd

    # Parse lvdisplay and vgdisplay strings and populate dictionaries with relevant information
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

    #
   # def GetTargets(self):
        #self.Exec(" ".join(['sudo', 'scstadmin','-w /etc/scst.conf']))
        #srv = pysftp.Connection(self.serverDNS,userName,keyFile)
        #srv.get('/etc/scst.conf','config/'+self.serverDNS+'.scst.conf')
   #     return 0

    # Update LV information, called to monitor and update capacity.
    def UpdateLVs(self,vgObject):
        lvdict = self.GetLVs()
        lvs = LV.objects.filter(vg=vgObject)
#        for eachLV in lvs:
#    	    if eachLV.lvname in lvdict:
#            	eachLV.lvsize=lvdict[eachLV.lvname]['LV Size']
#            	eachLV.lvthinmapped=lvdict[eachLV.lvname]['Mapped size']
#            	eachLV.save(update_fields=['lvsize','lvthinmapped'])
        for lvName,lvinfo in lvdict.iteritems():
            if len(lvs.filter(lvname=lvName)):
                preexistLV=lvs.filter(lvname=lvName)[0]
            	preexistLV.lvsize=lvinfo['LV Size']
            	preexistLV.lvthinmapped=lvinfo['Mapped size']
            	preexistLV.save(update_fields=['lvsize','lvthinmapped'])
            else:
                logger.warn("Found orphan LV %s in VG %s on host %s" %(lvName,self.vg,self.serverDNS))

    # Wrapper for parselvm (for LVs), actually populating the DB is done by the UpdateLV function
    def GetLVs(self,vguuid=None):
        if vguuid is None: 
            vguuid=self.vg  #kind of hack on the default arg - this is a vg uuid not a name in reality
        lvStrList = self.Exec(" ".join(['sudo','lvdisplay',vguuid]))
        delimitStr = '--- Logical volume ---'
        paraList=['LV Name','LV UUID','LV Size','Mapped size']
        lvs = self.ParseLVM(lvStrList,delimitStr,paraList)
        return lvs

    # Wrapper for parseLVM (for VGs)+populating the DB
    def GetVG(self): #Unit test this again
        vgStrList = self.Exec(" ".join(['sudo','vgdisplay','--units g',self.vg]))
        delimitStr = '--- Volume group ---'
        paraList=['VG Name','VG Size','PE Size','Total PE', 'Free  PE / Size', 'VG UUID']
        vgs = self.ParseLVM(vgStrList,delimitStr,paraList)
        try:
            cmdStr = self.Exec(" ".join(['sudo',self.remoteinstallLoc+'saturn-bashscripts/thinlvstats.sh']))
            logger.info(self.serverDNS+": "+" ".join(['sudo',self.rembashpath,self.remoteinstallLoc+'saturn-bashscripts/thinlvstats.sh'])+': LVS returned '+str(cmdStr))
            thinusedpercent = float(cmdStr[0].rstrip())
            thintotalGB = float(cmdStr[1].rstrip())
            maxthinavl = thintotalGB*(100-thinusedpercent)/100
        except:
            logger.warn("Unable to run LVScan on "+self.serverDNS)
            return -1
        logger.info(vgs)
        existingvgs = VG.objects.filter(vguuid=vgs[self.vg]['VG UUID'])
        if len(existingvgs)==1:
            existingvg = existingvgs[0]
            existingvg.CurrentAllocGB = Target.objects.filter(targethost=existingvg.vghost).aggregate(Sum('sizeinGB'))['sizeinGB__sum']
            existingvg.thinusedpercent=thinusedpercent
            existingvg.thintotalGB=thintotalGB
            existingvg.maxthinavlGB=maxthinavl
            existingvg.vgsize = vgs[self.vg]['VG Size']
            existingvg.save(update_fields=['thinusedpercent','thintotalGB','maxthinavlGB','vgsize','CurrentAllocGB'])
        else:
            myvg = VG(vghost=StorageHost.objects.get(dnsname=self.serverDNS),vgsize=vgs[self.vg]['VG Size'],
                    vguuid=vgs[self.vg]['VG UUID'],vgpesize=vgs[self.vg]['PE Size'],
                    vgtotalpe=vgs[self.vg]['Total PE'],
                    vgfreepe=vgs[self.vg]['Free  PE / Size'],
                    thinusedpercent=thinusedpercent,
                    thintotalGB=thintotalGB,maxthinavlGB=maxthinavl)
            myvg.save()#force_update=True)
        return vgs[self.vg]['VG UUID']

    #Check in changes to config files into git repository
    def GitSave(self,commentStr):
        srv = pysftp.Connection(self.serverDNS,self.userName,self.keyFile)
        srv.get('/temp/scst.conf',self.iscsiconfdir+self.serverDNS+'.scst.conf')
        srv.get('/temp/'+self.vg,self.iscsiconfdir+self.serverDNS+'.lvm')
        try:
            repo = Repo(self.iscsiconfdir)
            filelist = [ f for f in listdir(self.iscsiconfdir) if isfile(join(self.iscsiconfdir,f)) ]
            repo.stage(filelist)
            repo.do_commit(commentStr)
        except:
            var = traceback.format_exc()
            logger.warn("%s: Git save error: %s" % (commentStr,var))

    # Create iSCSI target by running the createtarget script; and save latest scst.conf from the remote server (overwrite)
    def CreateTarget(self,iqnTarget,iqnInit,sizeinGB,storageip1,storageip2):
        srv = pysftp.Connection(self.serverDNS,self.userName,self.keyFile)
        cmdStr = " ".join(['sudo',self.rembashpath,self.remoteinstallLoc+'saturn-bashscripts/createtarget.sh',str(sizeinGB),iqnTarget,storageip1,storageip2,iqnInit,self.vg])
        srv.close()
        #exStr = srv.execute(cmdStr)
        exStr=self.Exec(cmdStr)
        commentStr = "Trying to create target %s " %( iqnTarget, )
        self.GitSave(commentStr)
        logger.info("Execution report for %s:  %s" %(cmdStr,"\t".join(exStr)))
        if "SUCCESS" in str(exStr):
            logger.info("Returning successful createtarget run")
            return 1
        else:
            logger.info("Returning failed createtarget run")
            return 0

    # Read targets to determine their latest state via the parsetarget script
    def GetTargetsState(self):
        cmdStr = " ".join(["sudo",self.rempypath,self.remoteinstallLoc+'saturn-bashscripts/parsetarget.py'])
        exStr = self.Exec(cmdStr)
        for eachLine in exStr:
            iqntar=eachLine.split()[0]
            tar = Target.objects.filter(iqntar=iqntar)
            #logger.info("Matching targets for %s are: %s" % (iqntar,tar))
            if len(tar)==1:
                #logger.info("Found target %s on %s" %( iqntar,self.serverDNS) )
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
            else:
                logger.warn("Found target %s on %s that does not exist in the DB" % (iqntar,self.serverDNS) )

    # Delete target
    def DeleteTarget(self,iqntar):
        self.GetTargetsState()
        try:
            tar = Target.objects.get(iqntar=iqntar)
        except:
            logger.warn("Could not find deletion target in DB, exiting. "+iqntar)
            return -1
        if not tar.sessionup:
            cmdStr = " ".join(["sudo",self.rembashpath,self.remoteinstallLoc+'saturn-bashscripts/removetarget.sh',iqntar,self.vg])
            exStr = self.Exec(cmdStr)
            self.GitSave("Trying to delete  target %s " %( iqntar,))
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



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

#globalstatemanager/gsm.py

#remember to use at least pysftp 0.2.2 - i
#the pip install doesnt give you that version.
from pysftp import Connection
from os.path import dirname,join,basename,getsize,isfile
from os import listdir
from ConfigParser import RawConfigParser
from dulwich.repo import Repo
from django.core.management import execute_from_command_line
from django.db.models import Sum
from ssdfrontend.models import VG
from ssdfrontend.models import StorageHost
from ssdfrontend.models import LV
from ssdfrontend.models import Target
from ssdfrontend.models import Interface
from ssdfrontend.models import IPRange
from django.contrib.auth.models import User
from logging import getLogger
import utils.scstconf
import sys
from traceback import format_exc
from utils.configreader import ConfigReader
import socket
import ipaddress
reload (sys)
sys.setdefaultencoding("utf-8")
logger = getLogger(__name__)

class PollServer():
    """
    This is the controller that calls/runs scripts on a Saturn server
    as required by saturnring

    """
    def __init__(self,serverDNS):
        """
        The init script for the class
        """
        self.serverDNS = str(serverDNS)
        BASE_DIR = dirname(dirname(__file__))
        config = ConfigReader()
        self.userName = config.get('saturnnode','user')
        self.keyFile = join(BASE_DIR,config.get('saturnring','privatekeyfile'))
        self.rembashpath = config.get('saturnnode','bashpath')
        self.rempypath = config.get('saturnnode','pythonpath')
        self.iscsiconfdir = join(BASE_DIR,config.get('saturnring','iscsiconfigdir'))
        self.remoteinstallLoc = config.get('saturnnode','install_location')
        self.localbashscripts = join(BASE_DIR,config.get('saturnring','bashscripts'))
        try:
            self.srv = Connection(self.serverDNS,self.userName,self.keyFile)
        except:
            logger.critical("Failed SSH-exec connection on Saturn server %s; possible cause: %s" % (self.serverDNS,format_exc()) )
    

    def InstallScripts(self):
        """
        Copy bash scripts from the saturnringserver into the saturn server via sftp
        """
        #srv = Connection(self.serverDNS,self.userName,self.keyFile)
        self.srv.execute ('mkdir -p '+self.remoteinstallLoc+'saturn-bashscripts/')
        self.srv.chdir(self.remoteinstallLoc+'saturn-bashscripts/')
        locallist=listdir(self.localbashscripts)
        for localfile in locallist:
            self.srv.put(self.localbashscripts+localfile)
            self.srv.execute("chmod 777 "+join(self.remoteinstallLoc,'saturn-bashscripts',localfile))
        #srv.close()
        #Update rc.local for luks reboot functionality
        luksopenscriptpath = join(self.remoteinstallLoc,'saturn-bashscripts','luksonreboot.sh');
        self.srv.execute("sudo sed -i '/luksonreboot.sh/d' /etc/rc.local") #delete pre-existing line if any
        self.srv.execute("sudo sed -i '/^exit 0/i " + '/bin/bash ' + luksopenscriptpath +"' /etc/rc.local")
        logger.info("Installed scripts")


    def Exec(self,command):
        """
        Helper function for executing a remote command over an SSH tunnel
        """
        rtncmd = -1
        try:
            #srv = Connection(self.serverDNS,self.userName,self.keyFile)
            rtncmd=self.srv.execute(command)
            #srv.close()
        except:
            logger.error("Failed SSH-exec command: %s on Saturn server %s" % (command, self.serverDNS))
            logger.error(format_exc())
        return rtncmd

    def PutKeyFile(self,keyfileName):
        """
        Copy over the keyfile to be used for creating the LUKs encrypted DM volumes
        """
        remoteKeyfileDir = join(self.remoteinstallLoc,'keys')
        try:
            self.Exec ('mkdir -p ' + remoteKeyfileDir)
            self.srv.chdir(remoteKeyfileDir)
            self.srv.put(join(self.iscsiconfdir,keyfileName))
            self.remoteKeyfilePath = join(remoteKeyfileDir,keyfileName)
            rtnString = self.Exec ('test -f ' + self.remoteKeyfilePath + '&&  echo "OK Putkeyfile" ')
            logger.info(rtnString)
            if "OK Putkeyfile" not in str(rtnString):
                raise ValueError("Putkey didnt install file")
        except ValueError:
            logger.error("Failed to put keyfile on Saturn server %s at location %s" %(self.serverDNS,join(remoteKeyfileDir,keyfileName)))
            logger.error(format_exc())
            return -1

        return self.remoteKeyfilePath

    def DelKeyFile(self,keyfileName):
        """
        Delete key file from saturn server
        """
        remoteKeyfileDir = self.remoteinstallLoc+'/keys'
        self.srv.execute('rm '+ join(remoteKeyfileDir,keyfileName))
        rtnString = self.Exec ('test ! -f ' + join(self.iscsiconfdir,keyfileName)+ ' &&  echo "OK Deleted keyfile"')
        return rtnString


    def ParseLVM(self,strList,delimitStr,paraList):
        """
        Parse lvdisplay and vgdisplay strings and populate 
        dictionaries with relevant information
        """
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

        logger.info(rtnDict)
        return rtnDict


    def UpdateLVs(self,vgObject):
        """
        Update LV information, called to monitor and update capacity.
        """
        lvdict = self.GetLVs(vgObject.vguuid)
        if "No LVs " in lvdict:
            logger.info("There are no LVs in %s to run UpdateLVs on in Saturn host %s" %(vgObject.vguuid, self.serverDNS))
            return 0
        if lvdict == -1:
            logger.error ("Could not run GetLVs (perhaps there are no LVs in this VG yet?)")
            return -1
        lvs = LV.objects.filter(vg=vgObject)
        for lvName,lvinfo in lvdict.iteritems():
            if len(lvs.filter(lvname=lvName)):
                preexistLV=lvs.filter(lvname=lvName)[0]
            	preexistLV.lvsize=lvinfo['LV Size']
            	preexistLV.save(update_fields=['lvsize'])
            else:
                logger.warn("Found orphan LV %s in VG %s on host %s" %(lvName,vgObject.vguuid,self.serverDNS))


    def GetLVs(self,vguuid):
        """
        Wrapper for parselvm (for LVs), actually populating the DB is done by the UpdateLV function  
        """
        execCmd = " ".join(['sudo','vgdisplay', '-c','|','grep',vguuid,'|','cut -d: -f1'])
        vgname = self.Exec(execCmd)[0].strip()
        if vgname == -1:
            logger.error("Could not execute %s on %s " % (execCmd,self.serverDNS))
            return -1
        execCmd=" ".join(['sudo','lvdisplay','--units g',vgname])
        lvStrList = self.Exec(execCmd)
        if lvStrList ==[""]:
            return "No LVs in %s" %(vguuid,)

        if lvStrList == -1:
            logger.error("Could not execute %s on %s " % (execCmd,self.serverDNS))
            return -1
        delimitStr = '--- Logical volume ---'
        paraList=['LV Name','LV UUID','LV Size']
        lvs = self.ParseLVM(lvStrList,delimitStr,paraList)
        return lvs

    def GetVG(self): #Unit test this again
        """
        Wrapper for parseLVM (for VGs)+populating the DB
        """
        delimitStr = '--- Volume group ---'
        paraList = ['VG Name','VG Size','PE Size','Total PE', 'Free  PE / Size', 'VG UUID']
        execCmd = " ".join(['sudo','vgdisplay','--units g'])
        vgStrList = self.Exec(execCmd)
        if vgStrList == -1:
            return -1
        vgs = self.ParseLVM(vgStrList,delimitStr,paraList)
        #logger.info("VGStating on %s returns %s " % (self.serverDNS, str(vgs)) )
        rtnvguuidList = ""
        for vgname in vgs:
            try:
                execCmd = " ".join(['sudo',self.remoteinstallLoc+'saturn-bashscripts/vgstats.sh',vgname])
                cmdStr = self.Exec(execCmd)
                logger.info(self.serverDNS+": "+" ".join(['sudo',self.rembashpath,self.remoteinstallLoc+'saturn-bashscripts/vgstats.sh',vgname])+': returned '+str(cmdStr))
                maxavl = float(cmdStr[0].rstrip())
                totalGB = float(cmdStr[1].rstrip())
                isThin = bool(int(cmdStr[2].rstrip()))
            except:
                logger.warn("Unable to run VGscan, disabling VG on "+self.serverDNS)
                logger.warn(format_exc())
                try:
                    vg = VG.objects.get(vguuid=vgs[vgname]['VG UUID'])
                    vg.in_error = True
                    vg.save(update_fields=['in_error'])
                except:
                    logger.error("VG not found in DB: %s" % ( vgs[vgname]['VG UUID'],))
                return 3

            existingvgs = VG.objects.filter(vguuid=vgs[vgname]['VG UUID'])
            if len(existingvgs)==1:
                existingvg = existingvgs[0]
                existingvg.in_error=False
                existingvg.CurrentAllocGB = totalGB-maxavl#Target.objects.filter(targethost=existingvg.vghost).aggregate(Sum('sizeinGB'))['sizeinGB__sum']
                existingvg.totalGB=totalGB
                existingvg.maxavlGB=maxavl
                existingvg.is_thin=isThin
                existingvg.vgsize = vgs[vgname]['VG Size']
                existingvg.save(update_fields=['totalGB','maxavlGB','vgsize','CurrentAllocGB','in_error','is_thin'])
                logger.info( "Ran in existingVG loop")
            else:
                logger.info("Found new VG, adding\n" + str(vgs[vgname]))
                myvg = VG(vghost=StorageHost.objects.get(dnsname=self.serverDNS),vgsize=vgs[vgname]['VG Size'],
                        vguuid=vgs[vgname]['VG UUID'],vgpesize=vgs[vgname]['PE Size'],
                        vgtotalpe=vgs[vgname]['Total PE'],
                        vgfreepe=vgs[vgname]['Free  PE / Size'],
                        totalGB=totalGB,maxavlGB=maxavl, is_thin=isThin)
                myvg.save()#force_update=True)
            rtnvguuidList = rtnvguuidList+ ','+ vgs[vgname]['VG UUID']
        return rtnvguuidList[1:]

    
    def GitSave(self,vguuid,commentStr):
        """
        Check in changes to config files into git repository
        """
        try:
            #srv = Connection(self.serverDNS,self.userName,self.keyFile)
            self.srv.get('/temp/scst.conf',self.iscsiconfdir+self.serverDNS+'.scst.conf')
            self.srv.get('/temp/'+vguuid,self.iscsiconfdir+self.serverDNS+'.'+vguuid+'.lvm')
            try:
                repo = Repo(self.iscsiconfdir)
                filelist = [ f for f in listdir(self.iscsiconfdir) if isfile(join(self.iscsiconfdir,f)) ]
                repo.stage(filelist)
                repo.do_commit(commentStr)
            except:
                var = format_exc()
                logger.error("During GitSave: %s: Git save error: %s" % (commentStr, var))
        except:
            var = format_exc()
            logger.error("During GitSave: %s: PYSFTP download error: %s" % (commentStr, var))

    def CreateTarget(self,iqnTarget,iqnInit,sizeinGB,storageip1,storageip2,vguuid,isencrypted):
        """
        Create iSCSI target by running the createtarget script; 
        and save latest scst.conf from the remote server (overwrite)
        """
        #self.srv = Connection(self.serverDNS,self.userName,self.keyFile)
        if str(isencrypted) != '1':
            cmdStr = " ".join(['sudo',self.rembashpath,self.remoteinstallLoc+'saturn-bashscripts/createtarget.sh',
            str(sizeinGB),iqnTarget,storageip1,storageip2,iqnInit,vguuid])
        else:
            try:
                self.remotekeyfilelocation = self.PutKeyFile("cryptokey")
                cmdStr = " ".join(['sudo',self.rembashpath,self.remoteinstallLoc+'saturn-bashscripts/createencryptedtarget.sh',
                str(sizeinGB),iqnTarget,storageip1,storageip2,iqnInit,vguuid,self.remotekeyfilelocation])
                if self.remotekeyfilelocation == -1:
                    raise ValueError("Putkey failed")

            except:
                logger.error("Error setting up encrypted target: %s " %(iqnTarget,))
                logger.error(format_exc())
                return -1

        #srv.close()
        logger.info ("Launching createtarget with \n%s" %(cmdStr,))
        exStr=self.Exec(cmdStr)
        if exStr == -1:
            return -1

        commentStr = "Trying to create target %s " %( iqnTarget, )

        self.GitSave(vguuid,commentStr)
        logger.info("Execution report for %s:  %s" %(cmdStr,"\t".join(exStr)))
        if "SUCCESS" in str(exStr):
            logger.info("Returning successful createtarget run")
            return 1
        else:
            logger.error("Returning failed createtarget run")
            return 0

    def GetTargetsState(self):
        """
        Read targets to determine their latest state via the parsetarget script
        """
        cmdStr = " ".join(["sudo",self.rempypath,self.remoteinstallLoc+'saturn-bashscripts/parsetarget.py'])
        exStr = self.Exec(cmdStr)
        if exStr == -1:
            return -1
        for eachLine in exStr:
            iqntar = eachLine.split()[0]
            tar = Target.objects.filter(iqntar=iqntar)
            if len(tar)==1:
                tar = tar[0]
                if "no session" in eachLine:
                    tar.sessionup=False
                    tar.rkbpm = 0
                    tar.wkbpm = 0
                else:
                    tar.sessionup=True
                    rkb = long(eachLine.split()[1])
                    tar.rkbpm = long(rkb-tar.rkb)
                    tar.rkb=rkb
                    wkb = long(eachLine.split()[2])
                    wpm = long(wkb-tar.wkb)
                    tar.wkbpm = wpm
                    tar.wkb=wkb
                tar.save()
            else:
                logger.warn("Found target %s on %s that does not exist in the DB" % (iqntar,self.serverDNS) )

    def DeleteTarget(self,iqntar,vguuid):
        """
        Delete target
        """
        logger.info("Trying to delete target %s from VG %s on host %s" %(iqntar,vguuid,self.serverDNS))
        if self.GetTargetsState() == -1:
            logger.error("Could not GetTargetsState while deleting %s" %(iqntar,))
            return -1
        try:
            tar = Target.objects.get(iqntar=iqntar)
        except:
            logger.warn("Could not find deletion target in DB, exiting. "+iqntar)
            return -1
        if not tar.sessionup:
            cmdStr = " ".join(["sudo",self.rembashpath,self.remoteinstallLoc+'saturn-bashscripts/removetarget.sh',iqntar,vguuid])
            exStr = self.Exec(cmdStr)
            if exStr == -1:
                return -1
            self.GitSave(vguuid,"Trying to delete  target %s " %( iqntar,))
            success1 = False
            success2 = False
            for eachLine in exStr:
                logger.info(eachLine)
                if "Removing virtual target '"+iqntar+"' from driver 'iscsi': done" in eachLine:
                    success1=True
                if "successfully removed" in eachLine:
                    success2=True
            if success1==True and success2==True:
                logger.info("Successful deletion of target %s from VG %s on host %s" %(iqntar,vguuid,self.serverDNS))
                return 1
            else:
                logger.error("Error deleting target %s from VG %s on host %s" %(iqntar,vguuid,self.serverDNS))
                return -1
        else:
            logger.error("Target state of %s is set to session up, will not try to delete it." %(iqntar,))

        return -1

    def GetInterfaces(self):
        """
        Scan and get network interfaces into saturnring DB
        """
        #cmdStr = 'ifconfig | grep -oE "inet addr:[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}" | cut -d: -f2'
        cmdStr = 'ip addr | grep -oE "inet [0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}" | cut -d" "  -f2'
        ipadds=self.Exec(cmdStr)
        if ipadds == -1:
            return -1

        sh = StorageHost.objects.get(dnsname=self.serverDNS)
        superuser=User.objects.filter(is_superuser=True).order_by('username')[0]
        for addr in ipadds:
            try:
                addr = addr.rstrip()
                if "127.0.0.1" in addr: #Ignore loopback addresses
                    continue
                socket.inet_aton(addr)
                interfaces = Interface.objects.filter(ip=addr)
                if len(interfaces) != 1: #If 0, then new interface
                    Interface.objects.filter(ip=addr).delete()
                    logger.info("Adding newly discovered interface %s to storage host %s " % (addr, self.serverDNS))
                    try:
                        newInterface = Interface(storagehost=sh,ip=addr,owner=superuser)
                        newInterface.save()
                        for eachIPRange in IPRange.objects.all():
                            if ipaddress.ip_address(unicode(addr)) in ipaddress.ip_network(unicode(eachIPRange.iprange)):
                                eachIPRange.hosts.add(sh)
                                eachIPRange.save()
                                newInterface.iprange.add(eachIPRange)
                                newInterface.owner=eachIPRange.owner
                                newInterface.save()
                    except:
                        logger.warn("Error saving newly discovered Interface %s  of host %s" % (addr, self.serverDNS))
                        var = format_exc()
                        logger.warn(var)
                else:
                    if interfaces[0].storagehost.dnsname != self.serverDNS:
                        Interface.objects.filter(ip=addr).delete()
                        logger.warn("IP address %s was reassigned to another host" % (addr,))
            except socket.error:
                logger.warn("Invalid IP address %s retuned in GetInterfaces call on Saturn server %s " % (addr, self.serverDNS ))
                var = format_exc()
                logger.warn(var)

    def InsertCrypttab(self,base_LV,enc_LV,keyfilePath):
        """
        Insert entry into /etc/crypttab
        """
        baselvpath = self.Exec(" ".join(["sudo sh -c 'lvs -o lv_path | grep ",base_LV," | tr -d \" \"'"]))[0].strip()
        logger.info("BaseLVPATH = " + baselvpath)
        cmdStr = " ".join(["sudo sh -c 'echo \"" + enc_LV, baselvpath, keyfilePath, "luks\" >> /etc/crypttab'"])
        logger.info("InsertCrypttab: "+cmdStr)
        self.Exec(cmdStr)

    def DeleteCrypttab(self,lvStr):
        """
        Delete entry from /etc/crypttab
        LVStr can be either the encrypted LV name or the base LV name
        """
        cmdStr = " ".join(['sudo sed -i','/'+lvStr+'/d','/etc/crypttab'])
        logger.info("DeleteCrypttab: "+cmdStr)
        self.Exec(cmdStr)





#Commented out because there are formal unit tests.
#if __name__=="__main__":
#    pollserver = PollServer('saturnserver0.store.altus.bblabs')
#    cmdStr=pollserver.Exec("sudo /home/local/saturn/saturn-bashscripts/thinlvstats.sh")
#    print cmdStr



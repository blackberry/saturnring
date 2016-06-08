
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

import hashlib
from ssdfrontend.models import Target
from ssdfrontend.models import TargetNameMap
from ssdfrontend.models import LV
from ssdfrontend.models import VG
from ssdfrontend.models import AAGroup
from ssdfrontend.models import StorageHost
from ssdfrontend.models import TargetHistory
from ssdfrontend.models import ClumpGroup
from ssdfrontend.models import User
from ssdfrontend.models import Interface
from ssdfrontend.models import IPRange
from django.db.models import Sum
import django_rq
import ConfigParser
import os
import logging
import logging.handlers
from globalstatemanager.gsm import PollServer
from django.core.exceptions import ObjectDoesNotExist
from utils.scstconf import ParseSCSTConf
from django.db import connection
from traceback import format_exc
from os.path import join
import random
import string

def GenerateTargetName(clientiqn,targetHost,serviceName):
    clientiqnHash = hashlib.sha1(clientiqn).hexdigest()[:8]
    iqnTarget = "".join(["iqn.2014.01.",str(targetHost),":",serviceName,":",clientiqnHash])
    return iqnTarget

def CheckUserQuotas(storageSize,owner):
    logger = logging.getLogger(__name__)
    socketHandler = logging.handlers.SocketHandler('localhost',
                    logging.handlers.DEFAULT_TCP_LOGGING_PORT)
    logger.addHandler(socketHandler)

    user = User.objects.select_related('profile').get(username=owner)
    if (storageSize > user.profile.max_target_sizeGB):
        rtnStr = "User not authorized to create targets of %dGb, maximum size can be %dGb" %(storageSize,user.profile.max_target_sizeGB)
        return(-1,rtnStr)
    totalAlloc = Target.objects.filter(owner=owner).aggregate(Sum('sizeinGB'))
    if not totalAlloc['sizeinGB__sum']:
        totalAlloc['sizeinGB__sum'] = 0.0
    if (totalAlloc['sizeinGB__sum']+storageSize > user.profile.max_alloc_sizeGB):
        rtnStr = "User quota exceeded %dGb > %dGb" %(totalAlloc['sizeinGB__sum']+storageSize,user.profile.max_alloc_sizeGB)
        return (-1,rtnStr)
    return (1, "Quota checks ok, proceeding")

def ExecMakeTarget(storemedia,targetvguuid,targetHost,clientiqn,
        serviceName,storageSize,aagroup,clumpgroup,subnet,ownername,isencrypted):
    logger = logging.getLogger(__name__)
    socketHandler = logging.handlers.SocketHandler('localhost',
                    logging.handlers.DEFAULT_TCP_LOGGING_PORT)
    logger.addHandler(socketHandler)
    if 'iscsihypervisor' in serviceName:
        clientiqn = 'iqn.iscsihypervisor-'+clientiqn#+''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
    owner = User.objects.get(username=ownername)
    chosenVG=VG.objects.get(vguuid=targetvguuid)
    iqnTarget = GenerateTargetName(clientiqn,targetHost,serviceName)
    try:
        clientiqnHash = hashlib.sha1(clientiqn).hexdigest()[:8]
        targets = Target.objects.filter(iqntar__contains="".join([serviceName,":",clientiqnHash]))
        if len(targets) == 0:
            raise ObjectDoesNotExist
        for t in targets:
            iqnComponents = t.iqntar.split(':')
            if ((serviceName==iqnComponents[1]) and (clientiqnHash==iqnComponents[2])):
                logger.info('Target already exists for (serviceName=%s,clientiqn=%s) tuple' % (serviceName,clientiqn))
                try:
                    existingTargetstoremedia = LV.objects.get(target=t).vg.storemedia
                except:
                    logger.error("Target %s exists in DB but LV does not, inconsistent" %(t.iqntar))
                    return (-1,"Target %s exists in DB but LV does not, inconsistent" %(t.iqntar))

                if (existingTargetstoremedia=='unassigned') or (existingTargetstoremedia == storemedia):
                    return (1,t.iqntar)
                else:
                    errorStr = "Target %s on DIFFERENT storemedia %s already exists." % (t.iqntar,existingTargetstoremedia)
                    logger.info(errorStr)
                    return(-1,errorStr)
            else:
                raise ObjectDoesNotExist
    except ObjectDoesNotExist:
    #    try:
    #        if subnet != 'public':
    #            IPRange.objects.get(iprange=subnet)
    #    except:
    #        logger.debug('Subnet %s not found on host %s while trying to create target %s, creation aborted, contact admin' %(subnet, targetHost, iqnTarget ))
    #        return (-1,"Invalid subnet specified")

        (quotaFlag, quotaReason) = CheckUserQuotas(float(storageSize),owner)
        if quotaFlag == -1:
            logger.debug(quotaReason)
            return (-1,quotaReason)
        else:
            logger.info(quotaReason)
        logger.info("Creating new target for request {%s %s %s}, this is the generated iSCSItarget: %s" % (clientiqn, serviceName, str(storageSize), iqnTarget))
        targethost = StorageHost.objects.get(dnsname=targetHost)
        p = PollServer(targetHost)
        storeip1 = targethost.storageip1
        storeip2 = targethost.storageip2
        if subnet != 'public':
            try:
                storeip1 = Interface.objects.get(owner=owner,storagehost=targethost,iprange__iprange=unicode(subnet)).ip
                storeip2 = storeip1
            except:
                logger.error('Chosen host %s is missing IP addresses in requested subnet' % ( targethost, ) )
                return (-1, 'Error in host network configuration or ownership for the required subnet, contact storage admin')

        if p.CreateTarget(iqnTarget,clientiqn,str(storageSize),storeip1,storeip2,targetvguuid,isencrypted) == 1:
            logger.info ("SUCCESSFUL TARGET RUN")
            BASE_DIR = os.path.dirname(os.path.dirname(__file__))
            config = ConfigParser.RawConfigParser()
            config.read(os.path.join(BASE_DIR,'saturn.ini'))
            (devDic,tarDic)=ParseSCSTConf(os.path.join(BASE_DIR,config.get('saturnring','iscsiconfigdir'),targetHost+'.scst.conf'))
            #logger.info("DevDic = "+str(devDic))
            #logger.info("TarDic = "+str(tarDic))
            if iqnTarget in tarDic:
                newTarget = Target(owner=owner,targethost=targethost,iqnini=clientiqn,
                    iqntar=iqnTarget,sizeinGB=float(storageSize),storageip1=storeip1,storageip2=storeip2)
                if isencrypted == '1':
                    newTarget.isencrypted = True
                newTarget.save()

                lvDict=p.GetLVs(targetvguuid)
                lvName =  'lvol-'+hashlib.md5(iqnTarget+'\n').hexdigest()[0:8]
                logger.info("Looking for %s in lvDict %s" %(lvName, str(lvDict)))
                if lvName in lvDict:
                    newLV = LV(target=newTarget,vg=chosenVG,
                            lvname=lvName,
                            lvsize=storageSize,
                            #lvthinmapped=lvDict[lvName]['Mapped size'],
                            lvuuid=lvDict[lvName]['LV UUID'])

                    if isencrypted == '1':
                        newLV.isencrypted = True
                        p.InsertCrypttab(lvName,'encrypted_'+lvName,p.remotekeyfilelocation)
                    newLV.save()
                    chosenVG.CurrentAllocGB=max(0,chosenVG.CurrentAllocGB)+float(storageSize)
                    chosenVG.maxavlGB=max(0,chosenVG.maxavlGB-float(storageSize))
                    chosenVG.save()
            else:
                logger.error('Error - could not use ParseSCSTConf while working with target creation of %s, check if git and %s are in sync' % (iqnTarget, targethost.dnsname+'.scst.conf'))
                return (-1,"CreateTarget returned error 2, contact admin")

            tar = Target.objects.get(iqntar=iqnTarget)
            aa = AAGroup(name=aagroup,target=tar)
            aa.save()
            aa.hosts.add(targethost)
            aa.save()
            newTarget.aagroup=aa
            cg =ClumpGroup(name=clumpgroup,target=tar)
            cg.save()
            cg.hosts.add(targethost)
            cg.save()
            newTarget.clumpgroup=cg
            newTarget.save()
            connection.close() #close DB connection to prevent RQ connection reset error in PG database logs
            return (0,iqnTarget)
        else:
            connection.close() #close DB connection to prevent RQ connection reset error in PG database logs
            logger.error('CreateTarget did not work')
            return (-1,"CreateTarget returned error 1, contact admin")

def ExecChangeInitiator(iqntar,newini):
    logger = logging.getLogger(__name__)
    rtnVal = -1
    try:
        socketHandler = logging.handlers.SocketHandler('localhost',
                        logging.handlers.DEFAULT_TCP_LOGGING_PORT)
        logger.addHandler(socketHandler)
        target = Target.objects.get(iqntar=iqntar);
        p = PollServer(target.targethost)
        remotePath = join(p.remoteinstallLoc,'saturn-bashscripts','changeinitiator.sh')
        cmdStr = " ".join(['sudo', p.rembashpath, remotePath, iqntar, newini])
        rtncmd = p.Exec(cmdStr)
        if rtncmd == -1:
            raise Exception("Error while executing %s on iSCSI server %s."(cmdStr, target.targethost))
        if any("ALLOK"+iqntar in s for s in rtncmd):
            rtnVal = 0
            logger.info(str(rtncmd))
        else:
            raise Exception("Error while executing %s\n%s " %(cmdStr,str(rtncmd)))

    except:
        logger.error('Change initiator error in process thread')
        logger.error(format_exc())
        rtnVal = -1
    finally:
        return rtnVal

def ExecChangeTarget(oldtar,newtar,newini,allowedportal,ownername):
    logger = logging.getLogger(__name__)
    rtnVal = -1
    try:
        socketHandler = logging.handlers.SocketHandler('localhost',
                        logging.handlers.DEFAULT_TCP_LOGGING_PORT)
        logger.addHandler(socketHandler)

        owner = User.objects.get(username=ownername)
        oldtarget = Target.objects.get(iqntar = oldtar)
        lv = LV.objects.get(target=oldtarget)
        vg = lv.vg
        p = PollServer(oldtarget.targethost)
        remotePath = join(p.remoteinstallLoc,'saturn-bashscripts','renametarget.sh')
        cmdStr = " ".join(['sudo', p.rembashpath, remotePath, oldtar, str(newtar),vg.vguuid,str(lv),allowedportal,newini])
        rtncmd = p.Exec(cmdStr)
        if rtncmd == -1:
            raise Exception("Error while executing %s on iSCSI server %s."(cmdStr, target.targethost))
        if any("SUCCESS" in s for s in rtncmd):
            rtnVal = 0
            logger.info(str(rtncmd))
        else:
            raise Exception("Error while executing %s\n%s " %(cmdStr,str(rtncmd)))
    except:
        rtnStr = format_exc()
        logger.error(format_exc())
        return -1

    #Re-wire the database elements
    try:
        newtarget = Target(owner = owner,
                targethost = oldtarget.targethost,
                iqnini = newini,
                iqntar = newtar,
                sizeinGB = oldtarget.sizeinGB,
                rkb = oldtarget.rkb,
                rkbpm = oldtarget.rkbpm,
                wkb = oldtarget.wkb,
                wkbpm = oldtarget.wkbpm,
                created_at = oldtarget.created_at,
                storageip1 = allowedportal,
                isencrypted = oldtarget.isencrypted,
                pin = oldtarget.pin)
        newtarget.save()
        lv.target = newtarget
        lv.save()
        try:
            aag = AAGroup.objects.get(target=oldtarget)
            aag.target = newtarget
            aag.save()
        except:
            logger.warn(format_exc())
        try:
            cg = ClumpGroup.objects.get(target=oldtarget)
            cg.target = newtarget
            cg.save()
        except:
            logger.warn(format_exc())

        #Remember what was changed via this table
        newTargetNameMap = TargetNameMap(owner = owner,
                oldtarname = oldtar,
                newtarname = newtar)
        newTargetNameMap.save()

        #Delete old
        Target.objects.filter(iqntar=oldtarget.iqntar).delete()
        return 0
    except:
        logger.error("DB rewiring error: %s " %(str(format_exc(),)))
        return -1


def DeleteTargetObject(iqntar):
    obj = Target.objects.get(iqntar=iqntar)
    logger = logging.getLogger(__name__)
    socketHandler = logging.handlers.SocketHandler('localhost',
                    logging.handlers.DEFAULT_TCP_LOGGING_PORT)
    logger.addHandler(socketHandler)
    p = PollServer(obj.targethost)
    lv = LV.objects.get(target=obj)
    p.DeleteCrypttab(lv.lvname)
    if p.DeleteTarget(obj.iqntar,lv.vg.vguuid,lv.lvname)==1:
        newth=TargetHistory(owner=obj.owner,iqntar=obj.iqntar,iqnini=obj.iqnini,created_at=obj.created_at,sizeinGB=obj.sizeinGB,rkb=obj.rkb,wkb=obj.wkb)
        newth.save()
        tarVG = lv.vg
        tarVG.maxavlGB = tarVG.maxavlGB + obj.sizeinGB
        tarVG.save()
        obj.delete()
        connection.close() #close DB connection to prevent RQ connection reset error in PG database logs
        return 0
    else: 
        connection.close() #close DB connection to prevent RQ connection reset error in PG database logs
        return 1

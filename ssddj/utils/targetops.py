
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
from globalstatemanager.gsm import PollServer
from django.core.exceptions import ObjectDoesNotExist
from utils.scstconf import ParseSCSTConf

logger = logging.getLogger(__name__)

def CheckUserQuotas(storageSize,owner):
    user = User.objects.get(username=owner)
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

def ExecMakeTarget(storemedia,targetvguuid,targetHost,clientiqn,serviceName,storageSize,aagroup,clumpgroup,subnet,owner):
    chosenVG=VG.objects.get(vguuid=targetvguuid)
    clientiqnHash = hashlib.sha1(clientiqn).hexdigest()[:8]
    iqnTarget = "".join(["iqn.2014.01.",targetHost,":",serviceName,":",clientiqnHash])
    try:
        targets = Target.objects.filter(iqntar__contains="".join([serviceName,":",clientiqnHash]))
        if len(targets) == 0:
            raise ObjectDoesNotExist
        for t in targets:
            iqnComponents = t.iqntar.split(':')
            if ((serviceName==iqnComponents[1]) and (clientiqnHash==iqnComponents[2])):
                logger.info('Target already exists for (serviceName=%s,clientiqn=%s) tuple' % (serviceName,clientiqn))
                existingTargetstoremedia = LV.objects.get(target=t).vg.storemedia
                if (existingTargetstoremedia == storemedia):
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

        if (p.CreateTarget(iqnTarget,clientiqn,str(storageSize),storeip1,storeip2,targetvguuid)):
            BASE_DIR = os.path.dirname(os.path.dirname(__file__))
            config = ConfigParser.RawConfigParser()
            config.read(os.path.join(BASE_DIR,'saturn.ini'))
            (devDic,tarDic)=ParseSCSTConf(os.path.join(BASE_DIR,config.get('saturnring','iscsiconfigdir'),targetHost+'.scst.conf'))
            if iqnTarget in tarDic:
                newTarget = Target(owner=owner,targethost=targethost,iqnini=clientiqn,
                    iqntar=iqnTarget,sizeinGB=float(storageSize),storageip1=storeip1,storageip2=storeip2)
                newTarget.save()
                lvDict=p.GetLVs(targetvguuid)
                lvName =  'lvol-'+hashlib.md5(iqnTarget+'\n').hexdigest()[0:8]
                if lvName in lvDict:
                    newLV = LV(target=newTarget,vg=chosenVG,
                            lvname=lvName,
                            lvsize=storageSize,
                            lvthinmapped=lvDict[lvName]['Mapped size'],
                            lvuuid=lvDict[lvName]['LV UUID'])
                    newLV.save()
                    chosenVG.CurrentAllocGB=max(0,chosenVG.CurrentAllocGB)+float(storageSize)
                    chosenVG.save()

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

            return (0,iqnTarget)
        else:
            logger.warn('CreateTarget did not work')
            return (-1,"CreateTarget returned error, contact admin")


def DeleteTargetObject(obj):
    p = PollServer(obj.targethost)
    lv = LV.objects.get(target=obj)
    if p.DeleteTarget(obj.iqntar,lv.vg.vguuid)==1:
        newth=TargetHistory(owner=obj.owner,iqntar=obj.iqntar,iqnini=obj.iqnini,created_at=obj.created_at,sizeinGB=obj.sizeinGB,rkb=obj.rkb,wkb=obj.wkb)
        newth.save()
        obj.delete()
        return 0
    else:
        return 1

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

#api/viewhelper.py

from os.path import dirname,join
from ConfigParser import RawConfigParser
from time import sleep 
from logging import getLogger
from django_rq import get_queue
from django.contrib.auth.models import User
from operator import itemgetter
from ssdfrontend.models import Target
from ssdfrontend.models import StorageHost
from ssdfrontend.models import  VG
from ssdfrontend.models import LV
from ssdfrontend.models import AAGroup
from ssdfrontend.models import ClumpGroup
from ssdfrontend.models import Lock
from django.db.models import Sum
from django.db.models import Q
from django.db.models import F
from utils.targetops import DeleteTargetObject
from utils.scstconf import ParseSCSTConf
from utils.targetops import ExecMakeTarget
from hashlib import sha1
from traceback import format_exc
from utils.configreader import ConfigReader
def LVAllocSumVG(vg):
    '''
    Simple function to return sum of LV sizes in a specified VG
    '''
    lvs = LV.objects.filter(vg=vg)
    lvalloc=0.0
    for eachlv in lvs:
       lvalloc=lvalloc+eachlv.lvsize
    return lvalloc

def VGFilter(storageSize, aagroup,owner,clumpgroup="noclump",subnet="public",storemedia='pciessd'):
    '''
    The key filtering and "anti-affinity logic" function
    Check if StorageHost is enabled
    Check if VG is enabled
    Find all VGs where SUM(Alloc_LVs) + storageSize < opf*thintotalGB
    Further filter on whether thinusedpercent < thinusedmaxpercent
    Return a random choice from these
    Or do AAG logic
    '''
    logger = getLogger(__name__)
    storagehosts = StorageHost.objects.filter(enabled=True)
    logger.info("Found %d storagehosts" %(len(storagehosts),))
    qualvgs = []
    vgchoices = VG.objects.filter(in_error=False,is_locked=False,vghost__in=storagehosts,enabled=True,thinusedpercent__lt=F('thinusedmaxpercent'),storemedia=storemedia).order_by('?')#Random ordering here
    if len(vgchoices) > 0:
        numDel=0
        chosenVG = -1
        for eachvg in vgchoices:
            if subnet != "public":
                try:
                    eachvg.vghost.iprange_set.get(iprange=subnet,owner=owner)
                except:
                    var = format_exc()
                    logger.debug(var)
                    logger.info('Ignoring VG because subnet not in host or owner not authorized for this VG')
                    continue

            lvalloc = LVAllocSumVG(eachvg)
            eachvg.CurrentAllocGB=lvalloc
            eachvg.save()
            if (lvalloc + float(storageSize)) > (eachvg.thintotalGB*eachvg.opf):
               logger.info("Disqualified %s/%s, because %f > %f" %(eachvg.vghost,eachvg.vguuid,lvalloc+float(storageSize),eachvg.thintotalGB*eachvg.opf))
               numDel=numDel+1
            else:
                logger.info("A qualified choice for Host/VG is %s/%s" %(eachvg.vghost,eachvg.vguuid))
                if clumpgroup=="noclump":
                    if aagroup=="random":
                        return eachvg
                    else:
                        qualvgs.append((eachvg,eachvg.vghost.aagroup_set.all().filter(name=aagroup).count()))
                else:
                    qualvgs.append((eachvg,eachvg.vghost.clumpgroup_set.all().filter(name=clumpgroup).count()))
        if ( len(qualvgs) > 0 ) and (clumpgroup != "noclump"):
            chosenVG,overlap = sorted(qualvgs,key=itemgetter(1))[-1] #Chose host with maximum clump peers
            if overlap == 0:
                for ii in range(0,len(qualvgs)): #There is no clump peer, so need to fall back to aagroup
                    (vg,discardthis) = qualvgs[ii]
                    qualvgs[ii]= (vg,vg.vghost.aagroup_set.all().filter(name=aagroup).count())
                logger.info('No other clump peer found, falling back to AAgroup')
            else:
                logger.info('Clump group %s chose Saturn server %s, VG %s, with an overlap of %d.'%(clumpgroup,chosenVG.vghost,chosenVG.vguuid,overlap)) 
                return chosenVG

        if len(qualvgs) > 0:
            chosenVG,overlap =sorted(qualvgs, key=itemgetter(1))[0]
            logger.info('Anti-affinity group %s chose Saturn server %s with an overlap of %d.' %(aagroup,chosenVG.vghost,overlap))
            return chosenVG
        if len(vgchoices)>numDel:
            logger.info("Randomly chosen Host/VG combo is %s/%s" %(chosenVG.vghost,chosenVG.vguuid))
            return chosenVG
        else:
            logger.warn("No VG that satisfies the overprovisioning contraint (opf) was found")
            return -1
    else:
        logger.warn('No vghost/VG enabled')
        return -1
    logger.error('VG filter failed to find a suitable VG')
    return -1

def MakeTarget(requestDic,owner):
    """
    Actual maketarget orchestrator
    """
    logger = getLogger(__name__)
    clientiqn = requestDic['clientiqn']
    serviceName = requestDic['serviceName']
    storageSize = requestDic['sizeinGB']
    aagroup =''
    subnet=''
    if 'clumpgroup' not in requestDic:
        clumpgroup = "noclump"
    else:
        clumpgroup = requestDic['clumpgroup']

    if 'aagroup' not in requestDic:
        aagroup = "random"
    else:
        aagroup = requestDic['aagroup']

    if 'subnet' in requestDic:
        subnet = requestDic['subnet']
    else:
        subnet = "public"
    if 'storemedia' in requestDic:
        storemedia = requestDic['storemedia']
    else:
        storemedia = 'pciessd'

    logger.info("Provisioner - request received: ClientIQN: %s, Service: %s, Size(GB) %s, AAGroup: %s, Clumpgroup: %s, Subnet: %s " %(clientiqn, serviceName, str(storageSize), aagroup, clumpgroup, subnet))
    try:
        while 1:
            globallock = Lock.objects.get(lockname='allvglock')
            if globallock.locked==False:
                globallock.locked=True
                globallock.save()
                break
            else:
                sleep(0.2)
    except: #This is to create the lock the first time
        globallock = Lock(lockname='allvglock',locked=True)
        globallock.save()

    globallock = Lock.objects.get(lockname='allvglock')
    try:
        chosenVG = VGFilter(storageSize,aagroup,owner,clumpgroup,subnet,storemedia)
    except:
        logger.error("VGFilter broke")
        logger.error(format_exc())
        chosenVG = -1

    if chosenVG != -1:
        chosenVG.is_locked = True
        chosenVG.save(update_fields=['is_locked'])
        sleep(0.1) #Safety net to make sure the save did complete on the DB
        globallock.locked=False
        globallock.save()
        targetHost = str(chosenVG.vghost)
        targetvguuid = str(chosenVG.vguuid)
        config = ConfigReader()
        numqueues = config.get('saturnring','numqueues')
        queuename = 'queue'+str(hash(targetHost)%int(numqueues))
        queue = get_queue(queuename)
        logger.info("Launching create target job into queue %s" %(queuename,) )
        job = queue.enqueue(ExecMakeTarget,storemedia,targetvguuid,targetHost,clientiqn,serviceName,storageSize,aagroup,clumpgroup,subnet,owner)
        while 1:
            if job.result or job.is_failed:
                chosenVG.is_locked = False
                chosenVG.save(update_fields=['is_locked'])
                if job.is_failed:
                    return (-1,"Provisioner failed, check syntax or contact admin")
                return job.result
            else:
                sleep(0.25)
    else:
        globallock.locked=False
        globallock.save()
        try:
            clientiqnHash = hashlib.sha1(clientiqn).hexdigest()[:8]
            targets = Target.objects.filter(iqntar__contains="".join([serviceName,":",clientiqnHash]))
            if len(targets) != 0:
                for t in targets:
                    iqnComponents = t.iqntar.split(':')
                    if ((serviceName==iqnComponents[1]) and (clientiqnHash==iqnComponents[2])):
                        logger.info('Target already exists for (serviceName=%s,clientiqn=%s) tuple' % (serviceName,clientiqn))
                        return (1,t.iqntar)
        except:
            logger.warn("Something went wrong while checking for pre-existing target")

        logger.warn('VG filtering did not return a choice')
        return (-1, "Are Saturnservers online and adequate, contact admin")


def DeleteTarget(requestDic,owner):
    '''
    Delete iSCSI target
    This function dispatches a request to the worker queue of the Saturn host
    to delete the object (iSCSI target object).
    R: RequestDic - which may contain one of the following
    iqntarget name, 
    initiator name (all targets provisioned for that initiator),
    targethost (DNS name of Saturn server).

    '''
    logger = getLogger(__name__)
    queryset = None
    if 'iqntar' in requestDic:
        queryset=Target.objects.filter(iqntar=requestDic['iqntar'],owner=owner)
    if 'iqnini' in requestDic:
        if queryset is None:
            queryset=Target.objects.filter(iqnini=requestDic['iqnini'],owner=owner)
        else:
            queryset=queryset.objects.filter(iqnini=requestDic['iqnini'])
    if 'targethost' in requestDic:
        if queryset is None:
            queryset=Target.objects.filter(targethost=requestDic['targethost'],owner=owner)
        else:
            queryset=queryset.objects.filter(targethost=requestDic['targethost'])
    if queryset is None:
        return (1,"No targets to delete, or check delete API call")
    config = ConfigReader()
    numqueues = config.get('saturnring','numqueues')
    jobs =[]
    logger.info("DeleteTarget has %d targets to delete" % (queryset.count()))
    for obj in queryset:
        logger.info("DeleteTarget Working on deleting target %s" % (obj.iqntar,))
        queuename = 'queue'+str(hash(obj.targethost)%int(numqueues))
        queue = get_queue(queuename)
        jobs = []
        jobs.append( (queue.enqueue(DeleteTargetObject,obj), obj.iqntar) )
        logger.info("Using queue %s for deletion" %(queuename,))
    rtnStatus= {}
    rtnFlag=0
    numDone=0
    while numDone < len(jobs):
        ii=0
        sleep(1)
        for ii in range(0,len(jobs)):
            if jobs[ii] == 0:
                continue
            (job,target) = jobs[ii]
            if (job.result == 0) or (job.result == 1) or job.is_failed:
                if job.result==1 or job.is_failed:
                    logger.error("Failed deletion of " + target)
                    rtnStatus[target] = "Failed deletion of " + target
                rtnFlag=rtnFlag + job.result + int(job.is_failed)
                jobs[ii]=0
                numDone=numDone+1
            else:
                logger.info('...Working on deleting target '+target)
                break
    return (rtnFlag,str(rtnStatus))

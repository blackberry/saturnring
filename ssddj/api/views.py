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

from ssdfrontend.models import Target
from ssdfrontend.models import StorageHost
from ssdfrontend.models import LV
from ssdfrontend.models import VG
#from ssdfrontend.models import Provisioner
from ssdfrontend.models import AAGroup
from ssdfrontend.models import ClumpGroup
from ssdfrontend.models import Lock
from django.db.models import Sum
from django.contrib.auth.models import User
#from ssdfrontend.models import HostGroup
from operator import itemgetter
from globalstatemanager.gsm import PollServer
from serializers import TargetSerializer
from serializers import ProvisionerSerializer
from serializers import VGSerializer
from django.db.models import Q
from django.db.models import F
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.forms.models import model_to_dict
import random
import logging
from django.core import serializers
logger = logging.getLogger(__name__)
from utils.scstconf import ParseSCSTConf
from utils.periodic import UpdateState
from utils.periodic import UpdateOneState
from utils.targetops import ExecMakeTarget
from utils.targetops import DeleteTargetObject
import django_rq
import hashlib
import ConfigParser
import os
import time
def ValuesQuerySetToDict(vqs):
    return [item for item in vqs]

class UpdateStateData(APIView):
#    authentication_classes = (SessionAuthentication, BasicAuthentication)
#    permission_classes = (IsAuthenticated,)
    def get(self, request):
        BASE_DIR = os.path.dirname(os.path.dirname(__file__))
        config = ConfigParser.RawConfigParser()
        config.read(os.path.join(BASE_DIR,'saturn.ini'))
        numqueues = config.get('saturnring','numqueues')
        allhosts=StorageHost.objects.filter(enabled=True)
        for eachhost in allhosts:
            queuename = 'queue'+str(hash(eachhost)%int(numqueues))
            queue = django_rq.get_queue(queuename)
            queue.enqueue(UpdateOneState,eachhost)
        return Response("Ok, enqueued state update request")

class Delete(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    def get(self, request ):
        logger.info("Raw request data is "+str(request.DATA))
        (flag,statusStr) = self.DeleteTarget(request.DATA,request.user)
        logger.info("Deletion via API result" + str(statusStr))
        if flag!=0:
            rtnDict={}
            rtnDict['error']=1
            rtnDict['detail']=statusStr
            return Response(rtnDict,status=status.HTTP_400_BAD_REQUEST)
        else:
            rtnDict={}
            rtnDict['error']=0
            rtnDict['detail']=statusStr
            return Response(rtnDict,status=status.HTTP_200_OK)

    def DeleteTarget(self,requestDic,owner):
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
        BASE_DIR = os.path.dirname(os.path.dirname(__file__))
        config = ConfigParser.RawConfigParser()
        config.read(os.path.join(BASE_DIR,'saturn.ini'))
        numqueues = config.get('saturnring','numqueues')
        jobs =[]
        for obj in queryset:
            queuename = 'queue'+str(hash(obj.targethost)%int(numqueues))
            queue = django_rq.get_queue(queuename)
            jobs = []
            jobs.append( (queue.enqueue(DeleteTargetObject,obj), obj.iqntar) )
            logger.info("Using queue %s for deletion" %(queuename,))
        rtnStatus= {}
        rtnFlag=0
        numDone=0
        while numDone < len(jobs):
            ii=0
            time.sleep(1)
            for ii in range(0,len(jobs)):
                if jobs[ii] == 0:
                    continue
                (job,target) = jobs[ii]
                if (job.result == 0) or (job.result == 1):
                    if job.result==1:
                        logger.error('Failed deletion of '+target)
                    rtnStatus[target]="Error "+str(job.result)
                    rtnFlag=rtnFlag + job.result
                    jobs[ii]=0
                    numDone=numDone+1
                else:
                    logger.info('...Working on deleting target '+target)
                    break
        return (rtnFlag,str(rtnStatus))

class Provision(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    def get(self, request ):
        logger.info("Raw request data is "+str(request.DATA))
        serializer = ProvisionerSerializer(data=request.DATA)
        if serializer.is_valid():
            (flag,statusStr) = self.MakeTarget(request.DATA,request.user)
            if flag==-1:
                rtnDict = {}
                rtnDict['error']=1
                rtnDict['detail']=statusStr
                return Response(rtnDict, status=status.HTTP_400_BAD_REQUEST)
            if (flag==0 or flag==1):
                tar = Target.objects.filter(iqntar=statusStr)
                data = tar.values('iqnini','iqntar','sizeinGB','targethost','storageip1','storageip2','aagroup__name','clumpgroup__name','sessionup')
                rtnDict = ValuesQuerySetToDict(data)[0]
                rtnDict['targethost__storageip1']=rtnDict.pop('storageip1')
                rtnDict['targethost__storageip2']=rtnDict.pop('storageip2')

                rtnDict['already_existed']=flag
                rtnDict['error']=0
                return Response(rtnDict, status=status.HTTP_201_CREATED)
            else:
                rtnDict['error']=1
                rtnDict['detail'] = 'Problem provisioning, contact admin'
                return Response(rtnDict, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            logger.warn("Invalid provisioner serializer data: "+str(request.DATA))
            rtnDict={}
            rtnDict['error']=1
            rtnDict['detail']=serializer.errors
            return Response(rtnDict, status=status.HTTP_400_BAD_REQUEST)

    def LVAllocSumVG(self,vg):
        lvs = LV.objects.filter(vg=vg)
        lvalloc=0.0
        for eachlv in lvs:
           lvalloc=lvalloc+eachlv.lvsize
    	return lvalloc

    def VGFilter(self,storageSize, aagroup,owner,clumpgroup="noclump",subnet="public"):
        # Check if StorageHost is enabled
        # Check if VG is enabled
        # Find all VGs where SUM(Alloc_LVs) + storageSize < opf*thintotalGB
        # Further filter on whether thinusedpercent < thinusedmaxpercent
        # Return a random choice from these
        # Or do AAG logic
        storagehosts = StorageHost.objects.filter(enabled=True)
        logger.info("Found %d storagehosts" %(len(storagehosts),))
        qualvgs = []
        vgchoices = VG.objects.filter(in_error=False,is_locked=False,vghost__in=storagehosts,enabled=True,thinusedpercent__lt=F('thinusedmaxpercent')).order_by('?')#Random ordering here
        if len(vgchoices) > 0:
            numDel=0
            chosenVG = None
            for eachvg in vgchoices:
                if subnet != "public":
                    try:
                        eachvg.vghost.iprange_set.get(iprange=subnet,owner=owner)
                    except:
                        var = traceback.format_exc()
                        logger.debug(var)
                        logger.info('Ignoring VG because subnet not in host or owner not authorized for this VG')
                        continue

                lvalloc = self.LVAllocSumVG(eachvg)
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
                    logger.info('Clump group %s chose Saturn server %s with an overlap of %d.'%(clumpgroup,chosenVG.vghost,overlap)) 
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

    def MakeTarget(self,requestDic,owner):
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

        logger.info("Provisioner - request received: ClientIQN: %s, Service: %s, Size(GB) %s, AAGroup: %s, Clumpgroup: %s, Subnet: %s " %(clientiqn, serviceName, str(storageSize), aagroup, clumpgroup, subnet))
        try:
            while 1:
                globallock = Lock.objects.get(lockname='allvglock')
                if globallock.locked==False:
                    globallock.locked=True
                    globallock.save()
                    break
                else:
                    time.sleep(0.2)
        except:
            globallock = Lock(lockname='allvglock',locked=True)
            globallock.save()
        chosenVG = self.VGFilter(storageSize,aagroup,owner,clumpgroup,subnet)
        globallock = Lock.objects.get(lockname='allvglock')
        if chosenVG != -1:
            chosenVG.is_locked = True
            chosenVG.save(update_fields=['is_locked'])
            time.sleep(0.1) #Safety net to make sure the save did complete on the DB end
            globallock.locked=False
            globallock.save()
            targetHost=str(chosenVG.vghost)
            BASE_DIR = os.path.dirname(os.path.dirname(__file__)) 
            config = ConfigParser.RawConfigParser()
            config.read(os.path.join(BASE_DIR,'saturn.ini'))
            numqueues = config.get('saturnring','numqueues')
            queuename = 'queue'+str(hash(targetHost)%int(numqueues))
            queue = django_rq.get_queue(queuename)
            logger.info("Launching create target job into queue %s" %(queuename,) )
            job = queue.enqueue(ExecMakeTarget,targetHost,clientiqn,serviceName,storageSize,aagroup,clumpgroup,subnet,owner)
            while 1:
                if job.result:
                    chosenVG.is_locked = False
                    chosenVG.save(update_fields=['is_locked'])
                    return job.result
                else:
                    time.sleep(0.25)
        else:
            globallock.locked=False
            globallock.save()
            logger.warn('VG filtering did not return a choice')
            return (-1, "Are Saturnservers online and adequate, contact admin")

class VGScanner(APIView):
#    authentication_classes = (SessionAuthentication, BasicAuthentication)
#    permission_classes = (IsAuthenticated,)
    def get(self, request):
        logger.info("VG scan request received: %s " %(request.DATA,))
        saturnserver=request.DATA[u'saturnserver']
        if (StorageHost.objects.filter(Q(dnsname__contains=saturnserver) | Q(ipaddress__contains=saturnserver))):
            p = PollServer(saturnserver)
            savedvguuid = p.GetVG()
            readVG=VG.objects.filter(vguuid=savedvguuid).values()
            return Response(readVG)
        else:
            logger.warn("Unknown saturn server "+str(request.DATA))
            return Response("Unregistered or uknown Saturn server "+str(request.DATA), status=status.HTTP_400_BAD_REQUEST)


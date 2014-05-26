from ssdfrontend.models import Target
from ssdfrontend.models import StorageHost
from ssdfrontend.models import LV
from ssdfrontend.models import VG
#from ssdfrontend.models import Provisioner
from ssdfrontend.models import AAGroup

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
import django_rq
import hashlib
import ConfigParser
import os
def ValuesQuerySetToDict(vqs):
    return [item for item in vqs]

class UpdateStateData(APIView):
#    authentication_classes = (SessionAuthentication, BasicAuthentication)
#    permission_classes = (IsAuthenticated,)
    def get(self, request):
        queue = django_rq.get_queue('default')
        allhosts=StorageHost.objects.filter(enabled=True)
        for eachhost in allhosts:
            queue.enqueue(UpdateOneState,eachhost)
        return Response("Ok, enqueued state update request")

class Provision(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    def get(self, request ):
        logger.info("Raw request data is "+str(request.DATA))
        serializer = ProvisionerSerializer(data=request.DATA)
        if serializer.is_valid():
            #provfilter= Provisioner.objects.filter(clienthost=request.DATA[u'clienthost'],serviceName=request.DATA[u'serviceName'])
            #if len(provfilter):
            #    return Response("ERROR: Duplicate request, ignored")
            #else:
            (flag,statusStr) = self.MakeTarget(request.DATA,request.user)
            if flag==-1:
                rtnDict = {}
                rtnDict['error']=1
                rtnDict['detail']=statusStr
                return Response(rtnDict, status=status.HTTP_400_BAD_REQUEST)
            #serializer.save()
            if (flag==0 or flag==1):
                #tar = Target.objects.get(iqntar=statusStr)
                #rtnDict = model_to_dict(tar)
                #rtnDict['pre-existing']=flag
                #rtnDict.pop('owner',None)
                #return Response(rtnDict,status=status.HTTP_201_CREATED)

                tar = Target.objects.filter(iqntar=statusStr)
                data = tar.values('iqnini','iqntar','sizeinGB','targethost','targethost__storageip1','targethost__storageip2','aagroup__name','sessionup')
                rtnDict = ValuesQuerySetToDict(data)[0]
                rtnDict['already_existed']=flag
                rtnDict['error']=0
                return Response(rtnDict, status=status.HTTP_201_CREATED)
            else:
                rtnDict['error']=1
                rtnDict['detail'] = 'Problem provisioning, contact admin'
                return Response(rtnDict, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            logger.warn("Invalid provisioner serializer data: "+str(request.DATA))
            #rtnDict = ValuesQuerySetToDict(serializer.errors)
            rtnDict={}
            rtnDict['error']=1
            rtnDict['detail']=serializer.errors
            return Response(rtnDict, status=status.HTTP_400_BAD_REQUEST)

    def LVAllocSumVG(self,vg):
#        p = PollServer(vg.vghost) # Check this
 #       p.UpdateLVs(vg)
        lvs = LV.objects.filter(vg=vg)
        lvalloc=0.0
        for eachlv in lvs:
           lvalloc=lvalloc+eachlv.lvsize
    	return lvalloc
    

    def VGFilter(self,storageSize, aagroup):
        # Check if StorageHost is enabled
        # Check if VG is enabled
        # Find all VGs where SUM(Alloc_LVs) + storageSize < opf*thintotalGB
        # Further filter on whether thinusedpercent < thinusedmaxpercent
        # Return a random choice from these
        # Or do AAG logic
        storagehosts = StorageHost.objects.filter(enabled=True)
        logger.info("Found %d storagehosts" %(len(storagehosts),))
        qualvgs = []
        vgchoices = VG.objects.filter(enabled=True,thinusedpercent__lt=F('thinusedmaxpercent')).order_by('?')#Random ordering here
        if len(vgchoices) > 0:
            numDel=0
            chosenVG = None
            for eachvg in vgchoices:
                lvalloc = self.LVAllocSumVG(eachvg)
                eachvg.CurrentAllocGB=lvalloc
                eachvg.save()
                if (lvalloc + float(storageSize)) > (eachvg.thintotalGB*eachvg.opf):
                   logger.info("Disqualified %s/%s, because %f > %f" %(eachvg.vghost,eachvg.vguuid,lvalloc+float(storageSize),eachvg.thintotalGB*eachvg.opf))
                   numDel=numDel+1 
                else:
                    logger.info("A qualified choice for Host/VG is %s/%s" %(eachvg.vghost,eachvg.vguuid))
                    if aagroup=="random":
                        chosenVG = eachvg
                        break
                    else:
                        qualvgs.append((eachvg,eachvg.vghost.aagroup_set.all().filter(name=aagroup).count()))

            if len(qualvgs) > 0:
                chosenVG,overlap =sorted(qualvgs, key=itemgetter(1))[0]
                logger.info('Anti-affinity chose Saturn server %s with an overlap of %d.' %(chosenVG.vghost,overlap))
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

    def CheckUserQuotas(self,storageSize,owner):
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

    def MakeTarget(self,requestDic,owner):
        clientiqn = requestDic['clientiqn']
        serviceName = requestDic['serviceName']
        storageSize = requestDic['sizeinGB']
        if 'aagroup' not in requestDic:
            aagroup = "random"
        else:
            aagroup = requestDic['aagroup']
        logger.info("Provisioner - request received: ClientIQN: %s, Service: %s, Size(GB) %s, AAGroup: %s" %(clientiqn, serviceName, str(storageSize), aagroup))
        (quotaFlag, quotaReason) = self.CheckUserQuotas(float(storageSize),owner)
        if quotaFlag == -1:
            logger.debug(quotaReason)
            return (-1,quotaReason)
        else:
            logger.info(quotaReason)
        
        chosenVG = self.VGFilter(storageSize,aagroup)
        if chosenVG <> -1:
            targetHost=str(chosenVG.vghost)
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
                        return (1,t.iqntar)
                    else:
                        raise ObjectDoesNotExist
            except ObjectDoesNotExist:
                logger.info("Creating new target for request {%s %s %s}, this is the generated iSCSItarget: %s" % (clientiqn, serviceName, str(storageSize), iqnTarget))
                targetIP = StorageHost.objects.get(dnsname=targetHost)
                p = PollServer(targetHost)
                if (p.CreateTarget(iqnTarget,clientiqn,str(storageSize),targetIP.storageip1,targetIP.storageip2)):
                    #p.GetTargets()
                    BASE_DIR = os.path.dirname(os.path.dirname(__file__)) 
                    config = ConfigParser.RawConfigParser()
                    config.read(os.path.join(BASE_DIR,'saturn.ini'))			
                    (devDic,tarDic)=ParseSCSTConf(os.path.join(BASE_DIR,config.get('saturnring','iscsiconfigdir'),targetHost+'.scst.conf'))
#                    logger.info("Got devDic via parsescst:")
#                    logger.info(devDic)
#                    logger.info("Got tarDic via parsescst:")
#                    logger.info(tarDic)
                    if iqnTarget in tarDic:
                        newTarget = Target(owner=owner,targethost=chosenVG.vghost,iqnini=clientiqn,
                            iqntar=iqnTarget,sizeinGB=float(storageSize))
                        newTarget.save()
                        lvDict=p.GetLVs()
#                        logger.info("Got LVDICT on 203/api/views.py:")
#                        logger.info(lvDict)
                        lvName =  'lvol-'+hashlib.md5(iqnTarget+'\n').hexdigest()[0:8]
#                        logger.info("lvol name should be: %s" %(lvName,))
                        if lvName in lvDict:
                            newLV = LV(target=newTarget,vg=chosenVG,
                                    lvname=lvName,
                                    lvsize=storageSize,
                                    lvthinmapped=lvDict[lvName]['Mapped size'],
                                    lvuuid=lvDict[lvName]['LV UUID'])
                            newLV.save()
                            chosenVG.CurrentAllocGB=chosenVG.CurrentAllocGB+float(storageSize)
                            chosenVG.save()

                    if 'aagroup' in requestDic:
                        aagroup = requestDic['aagroup']
                        tar = Target.objects.get(iqntar=iqnTarget)
                        aa = AAGroup(name=requestDic['aagroup'],target=tar)
                        aa.save()
                        aa.hosts.add(chosenVG.vghost)
                        aa.save()
                        newTarget.aagroup=aa
                        newTarget.save()

                    return (0,iqnTarget)
                else:
                    logger.warn('CreateTarget did not work')
                    return (-1,"CreateTarget returned error, contact admin")
        else:
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


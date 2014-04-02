from ssdfrontend.models import Target
from ssdfrontend.models import StorageHost
from ssdfrontend.models import LV
from ssdfrontend.models import VG
from ssdfrontend.models import Provisioner
from ssdfrontend.models import AAGroup
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
import random
import logging
from django.core import serializers
logger = logging.getLogger(__name__)
from utils.scstconf import ParseSCSTConf
from utils.periodic import UpdateState
import django_rq

class UpdateStateData(APIView):
#    authentication_classes = (SessionAuthentication, BasicAuthentication)
#    permission_classes = (IsAuthenticated,)
    def get(self, request):
        queue = django_rq.get_queue('default')
        queue.enqueue(UpdateState)
        logger.info("Updating cluster global state")
        return Response("Ok, enqueued state update request")

class Provision(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    def get(self, request ):
        serializer = ProvisionerSerializer(data=request.DATA)
        if serializer.is_valid():
            provfilter= Provisioner.objects.filter(clienthost=request.DATA[u'clienthost'],serviceName=request.DATA[u'serviceName'])
            if len(provfilter):
                return Response("\nERROR: Duplicate request, ignored\n")
            else:
                iqntar = self.MakeTarget(request.DATA,request.user)
                serializer.save()
                if iqntar <> 0:
                    tar = Target.objects.filter(iqntar=iqntar)
                    data = tar.values('iqnini','iqntar','sizeinGB','targethost','targethost__storageip1','targethost__storageip2','aagroup__name')
                    return Response(data[0], status=status.HTTP_201_CREATED)
                else:
                    return Response(serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            logger.warn("Invalid provisioner serializer data: "+str(request.DATA))
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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

    def MakeTarget(self,requestDic,owner):
        clientStr = requestDic['clienthost']
        serviceName = requestDic['serviceName']
        storageSize = requestDic['sizeinGB']
        if 'aagroup' not in requestDic:
            aagroup = "random"
        else:
            aagroup = requestDic['aagroup']
        logger.info("Provisioner - request received: Client: %s, Service: %s, Size(GB) %s, AAGroup: %s" %(clientStr, serviceName, str(storageSize), aagroup))
        chosenVG = self.VGFilter(storageSize,aagroup)
        if chosenVG <> -1:
            targetHost=str(chosenVG.vghost)
            iqnTarget = "".join(["iqn.2014.01.",targetHost,":",serviceName,":",clientStr])
            try:
                t = Target.objects.get(iqntar=iqnTarget)
                logger.info('Target already exists: %s' % (iqnTarget,))
                return iqnTarget
            except ObjectDoesNotExist:
                logger.info("Creating new target for request {%s %s %s}, this is the generated iSCSItarget: %s" % (clientStr, serviceName, str(storageSize), iqnTarget))
                targetIP = StorageHost.objects.get(dnsname=targetHost)
                p = PollServer(targetIP.ipaddress)
                if (p.CreateTarget(iqnTarget,str(storageSize),targetIP.storageip1,targetIP.storageip2)):
                    #p.GetTargets()
                    (devDic,tarDic)=ParseSCSTConf('config/'+targetIP.ipaddress+'.scst.conf')
                    if iqnTarget in tarDic:
                        newTarget = Target(owner=owner,targethost=chosenVG.vghost,iqnini=iqnTarget+":ini",
                            iqntar=iqnTarget,clienthost=clientStr,sizeinGB=float(storageSize))
                        newTarget.save()
                        lvDict=p.GetLVs()
                        if devDic[tarDic[iqnTarget][0]] in lvDict:
                            newLV = LV(target=newTarget,vg=chosenVG,
                                    lvname=devDic[tarDic[iqnTarget][0]],
                                    lvsize=storageSize,
                                    lvthinmapped=lvDict[devDic[tarDic[iqnTarget][0]]]['Mapped size'],
                                    lvuuid=lvDict[devDic[tarDic[iqnTarget][0]]]['LV UUID'])
                            newLV.save()
                            chosenVG.CurrentAllocGB=chosenVG.CurrentAllocGB+float(storageSize)
                            chosenVG.save()

                    if 'aagroup' in requestDic:
                        aagroup = requestDic['aagroup']
                        aa = AAGroup(name=requestDic['aagroup'])
                        aa.save()
                        aa.hosts.add(chosenVG.vghost)
                        aa.save()
                        newTarget.aagroup=aa
                        newTarget.save()

                    return iqnTarget
                else:
                    logger.warn('CreateTarget did not work')
                    return 0
        else:
            logger.warn('VG filtering did not return a choice')
            return  "No suitable Saturn server was found to accomadate your request"

class VGScanner(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
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

class TargetDetail(APIView):
    """
    Retrieve, update or delete a target instance.
    """
    def get_object(self, pk):
        try:
            return Target.objects.get(pk=pk)
        except Target.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        target = self.get_object(pk)
        serializer = TargetSerializer(target)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        target = self.get_object(pk)
        serializer = TargetSerializer(target, data=request.DATA)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        target = self.get_object(pk)
        target.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


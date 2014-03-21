from ssdfrontend.models import Target
from ssdfrontend.models import StorageHost
from ssdfrontend.models import LV
from ssdfrontend.models import VG
from globalstatemanager.gsm import PollServer
from utils.affinity import RandomAffinity
from serializers import TargetSerializer
from serializers import ProvisionerSerializer

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
logger = logging.getLogger(__name__)
from utils.scstconf import ParseSCSTConf
class Provisioner(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    def get(self, request ):
        serializer = ProvisionerSerializer(data=request.DATA)
        if serializer.is_valid():
            iqntar = self.MakeTarget(request.DATA,request.user)
            serializer.save()
            if iqntar <> 0:
                tar = Target.objects.filter(iqntar=iqntar)
                data = tar.values()
                #data = serializers.serialize('json', list(Target.objects.get(iqntar=iqntar)), fields=('iqnini','iqntar'))a
                return Response(data, status=status.HTTP_201_CREATED)
            else:
                return Response(TargetSerializer.errors, status = status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            logger.warn("Invalid provisioner serializer data: "+str(request.DATA))
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def MakeTarget(self,requestDic,owner):
        clientStr = requestDic['clienthost']
        serviceName = requestDic['serviceName']
        storageSize = requestDic['sizeinGB']
        #first query each host for vg capacity(?)
        #do this in parallel using a thread per server
        logger.info("Provisioner - request received: %s %s %s" %(clientStr, serviceName, str(storageSize)))
        vgchoices = VG.objects.filter(maxthinavlGB__gt=float(storageSize))
        logger.info("VG choices are %s " %(str(vgchoices),))
        chosenVG = random.choice(vgchoices)
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
            if (p.CreateTarget(iqnTarget,str(storageSize))):
                p.GetTargets()
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
                
                return iqnTarget
            else:
                return 0

class VGScanner(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        logger.info("VG scan request received: %s " %(request.DATA,))
        sg = StorageHost.get(dnsname=request.DATA.saturnserver)
        p = PollServer(sg.ipaddress)
        p.GetVG()
        return (Response("OK"))

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


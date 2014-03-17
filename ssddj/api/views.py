from logmodule.thelogger import theLogger
from ssdfrontend.models import Target
from ssdfrontend.models import StorageHost
from ssdfrontend.models import LV
from ssdfrontend.models import VG

from serializers import TargetSerializer
from serializers import ProvisionerSerializer

from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
import random

lp = theLogger('API - View - Provisioner','config/logconfig.yml')
class Provisioner(APIView):

    def get(self, request ):
        serializer = ProvisionerSerializer(data=request.DATA)
        lp.logger.info(str(request.DATA))
        if serializer.is_valid():
            self.GenerateTargetIQN(request.DATA)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            lp.logger.warn("Invalid provisioner serializer data: "+str(request.DATA))
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def GenerateTargetIQN(self,requestDic):
        lp.logger.info(str(requestDic))
        clientStr = requestDic['clienthost']
        serviceName = requestDic['serviceName']
        storageSize = requestDic['sizeinGB']
        lp.logger.info("Provisioner - request received: %s %s %s" %(clientStr, serviceName, str(storageSize)))
        vgchoices = VG.objects.filter(vgfreepe__gt=float(storageSize)*0.004)
        lp.logger.info("VG choices are %s " %(str(vgchoices),))
        chosenVG = random.choice(vgchoices)
        targetHost=str(chosenVG.vghost)
        iqnTarget = "".join(["iqn.2014.01.",targetHost,":",serviceName,":",clientStr])
        lp.logger.info("This is the iSCSItarget: %s " % (iqnTarget,))
        #lp.logger.info("Shortlisted these VGs: "+ str(VG.objects.filter(vgpesize*vgfreepe < float(storageSize))))


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


from ssdfrontend.models import Target
from serializers import TargetSerializer
from serializers import ProvisionerSerializer
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from logmodule.thelogger import theLogger
from django.views.decorators.csrf import csrf_exempt

class Provisioner(APIView):
    def __init__(self, name=None, *args):
        self.l = theLogger('API - View - Provisioner','config/logconfig.yml')

    def get(self, request ):
        serializer = ProvisionerSerializer(data=request.DATA)
        if serializer.is_valid():
            serializer.save()
            self.GenerateTargetIQN(request.DATA)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            self.l.logger.warn("Invalid provisioner serializer data: "+str(request.DATA))
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def GenerateTargetIQN(self,requestDic):
        clientStr = requestDic['clienthost'][0]
        serviceName = requestDic['serviceName'][0]
        storageSize = requestDic['sizeinGB'][0]
        self.l.logger.info("Provisioner - request received: "+str(requestDic))



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


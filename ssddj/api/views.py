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
#from ssdfrontend.models import Provisioner
from django.contrib.auth.models import User
#from ssdfrontend.models import HostGroup
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
import logging
from django.core import serializers
logger = logging.getLogger(__name__)
from .viewhelper import DeleteTarget
from .viewhelper import VGFilter
from .viewhelper import MakeTarget
from utils.periodic import UpdateState
from utils.periodic import UpdateOneState
import django_rq
import ConfigParser
import os
import time
import traceback
from utils.reportmaker import StatMaker
import mimetypes
from django.core.servers.basehttp import FileWrapper
from django.http import HttpResponse
import traceback
import json
def ValuesQuerySetToDict(vqs):
    return [item for item in vqs]

class ReturnStats(APIView):
    def get(self, request):
        try:
            error = StatMaker()
            BASE_DIR = os.path.dirname(os.path.dirname(__file__))
            config = ConfigParser.RawConfigParser()
            config.read(os.path.join(BASE_DIR,'saturn.ini'))
            thefile = os.path.join(config.get('saturnring','iscsiconfigdir'),config.get('saturnring','clustername')+'.xls')
            filename = os.path.basename(thefile)
            response = HttpResponse(FileWrapper(open(thefile)),content_type=mimetypes.guess_type(thefile)[0])
            response['Content-Length'] = os.path.getsize(thefile)
            response['Content-Disposition'] = "attachment; filename=%s" % filename
            return response
        except:
            var = traceback.format_exc()
            logger.warn("Stat error: %s" % (var,))
            return Response(time.strftime('%c')+": Stat creation error: contact administrator")


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
        (flag,statusStr) = DeleteTarget(request.DATA,request.user)
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


class Provision(APIView):
    """
    Provision API call 
    """
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    def get(self, request ):
        logger.info("Raw request data is "+str(request.DATA))
        serializer = ProvisionerSerializer(data=request.DATA)
        if serializer.is_valid():
            (flag,statusStr) = MakeTarget(request.DATA,request.user)
            if flag==-1:
                rtnDict = {}
                rtnDict['error']=1
                rtnDict['detail']=statusStr
                return Response(rtnDict, status=status.HTTP_400_BAD_REQUEST)
            if (flag==0 or flag==1):
                tar = Target.objects.filter(iqntar=statusStr)
                data = tar.values('iqnini','iqntar','sizeinGB','targethost','storageip1','storageip2','aagroup__name','clumpgroup__name','sessionup')
                rtnDict = ValuesQuerySetToDict(data)[0]
                rtnDict['targethost__storageip1']=rtnDict.pop('storageip1') #in order to not change the user interface
                if rtnDict['targethost__storageip1']=='127.0.0.1':
                    rtnDict['targethost__storageip1']= tar[0].targethost.storageip1
                rtnDict['targethost__storageip2']=rtnDict.pop('storageip2')
                if rtnDict['targethost__storageip2']=='127.0.0.1':
                    rtnDict['targethost__storageip2']= tar[0].targethost.storageip2
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


class VGScanner(APIView):
#    authentication_classes = (SessionAuthentication, BasicAuthentication)
#    permission_classes = (IsAuthenticated,)
    def get(self, request):
        logger.info("VG scan request received: %s " %(request.DATA,))
        saturnserver=request.DATA[u'saturnserver']
        if (StorageHost.objects.filter(Q(dnsname__contains=saturnserver) | Q(ipaddress__contains=saturnserver))):
            p = PollServer(saturnserver)
            savedvguuidStr = p.GetVG()
            if type(savedvguuidStr) is not str:
                logger.warn('GetVG returned error integer: ' + str(savedvguuidStr))
                return Response('Error scanning VG, contact admin:')
            listvguuid = savedvguuidStr.split(',')
            readVG = VG.objects.filter(vguuid__in=listvguuid).values('vguuid','vghost')
            return Response(readVG)
            logger.info("RETURNING THIS "+str(readVG))
            #return savedvguuidStr
        else:
            logger.warn("Unknown saturn server "+str(request.DATA))
            return Response("Unregistered or uknown Saturn server "+str(request.DATA), status=status.HTTP_400_BAD_REQUEST)


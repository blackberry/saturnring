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

#api/views.py
from time import sleep,strftime,gmtime
from django.contrib.auth.models import User
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
from logging import getLogger
from django.core import serializers
#from utils.periodic import UpdateState
from utils.periodic import UpdateOneState
from django_rq import get_queue
from ConfigParser import RawConfigParser
from os.path import dirname,join,basename,getsize
from time import strftime
from traceback import format_exc
from utils.reportmaker import StatMaker
from mimetypes import guess_type
#from django.core.servers.basehttp import FileWrapper
from django.http import HttpResponse
from ssdfrontend.models import Target
from ssdfrontend.models import StorageHost
from ssdfrontend.models import VG
from globalstatemanager.gsm import PollServer
from .viewhelper import DeleteTarget
from .viewhelper import VGFilter
from .viewhelper import MakeTarget
from .viewhelper import UserStats
from .viewhelper import TargetPortal
from .viewhelper import ChangeInitiatorHelper
from .viewhelper import ChangeTargetHelper
from utils.configreader import ConfigReader

def ValuesQuerySetToDict(vqs):
    """
    Helper to convert queryset to dictionary
    """
    return [item for item in vqs]

class ReturnUserStats(APIView):
    """
    /api/userstats/

    Returns the user's assigned quota and the currently used quota in GB.

    Requires authenticated user.
    
    Example usage:
    
    curl -X GET http://saturnring.example.com/api/userstats/ --user "userid:password"

    {"total": 4.0, "used": 1.0, "error": 0}
    """
    def __getstate__(self):
        d = dict(self.__dict__)
        del d['logger']
        return d

    def __setstate__(self, d):
        self.__dict__.update(d)
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        logger = getLogger(__name__)
        (rtnVal,output)= UserStats(request.user)
        if rtnVal == -1:
            logger.warn("Error checking quota")
            return Response({'error':1, 'errorstring':output}, status=status.HTTP_400_BAD_REQUEST)
        else:
            (total,used) = output;
            return Response({'error':0,'total':total,'used':used})

class ReturnTargetPortal(APIView):
    """
    /api/targetportal/

    Return the specified target's portal IP address (this is the storageip_1 field)

    Requires a valid iSCSI target FQDN on the Saturnring server.

    Example usage:

    curl  -X GET http://saturnring.example.com/api/targetportal/  --data "iqntar=<target_IQN>"

    {"portal": "192.168.50.51", "error": 0}

    """
    def __getstate__(self):
        d = dict(self.__dict__)
        del d['logger']
        return d

    def __setstate__(self, d):
        self.__dict__.update(d)
    def get(self, request):
        logger = getLogger(__name__)
        (rtnVal,outstr) = TargetPortal(request.data)
        if rtnVal == -1:
            logger.warn("Error returning portal IP")
            return Response({'error':1, 'error_string':outstr }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error':0,'portal':outstr})

class ChangeInitiator(APIView):
    """
    NOTE: disabled in the urls.py as of 10.19.2015. 
    /api/changeinitiator/

    Change the initiator (clientiqn or iqnini) of a target in SCST. Returns error if target has an active session
    target

    Requires a valid current target name "iqntar" and new initiatorname "newini" of the form "iqn.*.ini"

    Example usage:

    curl -X GET http://saturnring.example.com/api/changeinitiator/ 
    
    --data "newini=iqn.unique_string_initiator.ini"

    --data "iqntar=iqn.existing_target.ini"

    """
    def __getstate__(self):
        d = dict(self.__dict__)
        del d['logger']
        return d

    def __setstate__(self, d):
        self.__dict__.update(d)
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        logger = getLogger(__name__)
        (rtnVal,errorstring) = ChangeInitiatorHelper(request.data,request.user)
        if rtnVal == -1:
            logger.error("Could not change initiator name.")
            return Response({'error':1, 'error_string':"Error reassigning initiator: " + errorstring}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error':0})


class ChangeTarget(APIView):
    """ 
    /api/changetarget/



    Changing the Target name.This means a new initiatorname and new service name are supplied, and 
    saturnring creates a new target name and completes all backend changes (SaturnringDB, SCST configuration)
    
    The process of changing the target name is as follows:
    1. Verify that the "old target" actually exists
    2. Verify change pin is correct.
    3. Use the new service name and new initiator name to create the new target name
    4. Rename the target on the SCST config file
    5. Create a new Target record in the DB, populating most of it from the old target record
    6. Point the LV, AAgroup, and Clumpgroup (which have Target as a foreign key) to the new Target record
    7. Make an entry in TargetNameMap table about the change
    8. Delete old target DB record
    """
    def __getstate__(self):
        d = dict(self.__dict__)
        del d['logger']
        return d

    def __setstate__(self, d):
        self.__dict__.update(d)
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        try:
            logger = getLogger(__name__)
            (rtnVal,rtnString) = ChangeTargetHelper(request.data,request.user)
            if rtnVal < 0:
                logger.error("Could not change target name.")
                return Response({'error':1, 'error_string':"Error reassigning target name, details: %s" %(rtnString,)}, status=status.HTTP_400_BAD_REQUEST)
            else:
                storeip1 = str(Target.objects.get(iqntar=rtnString).storageip1)
                return Response({'error':0,'iqntar':rtnString,'targethost__storageip1':storeip1})
        except:
            logger.error(format_exc)


class ReturnStats(APIView):
    """
    CBV for returning an excel-file containing the statistics of the Saturn cluster
    /api/stats
    Does not require authenticated user
    """
    def get(self, request):
        logger = getLogger(__name__)
        try:
            error = StatMaker()
            if error != 0:
               logger.error('Stat creation returned'+str(error))
               raise IOError

            config = ConfigReader()
            thefile = join(config.get('saturnring','iscsiconfigdir'),config.get('saturnring','clustername')+'.xls')
            filename = basename(thefile)
            response = HttpResponse(open(thefile),content_type=guess_type(thefile)[0]) #removed filewrapper around thefile
            response['Content-Length'] = getsize(thefile)
            response['Content-Disposition'] = "attachment; filename=%s" % filename
            return response
        except:
            var = format_exc()
            logger.warn("Stat error: %s" % (var,))
            return Response(strftime('%c')+": Stat creation error: contact administrator")

class UpdateStateData(APIView):
    """
    Runs a stateupdate script on all the saturn servers in the cluster
    Does not require authenticated user
    /api/stateupdate
    """
    #Inserted get and set state for pickle issues of the logger object
    def __getstate__(self):
        d = dict(self.__dict__)
        del d['logger']
        return d

    def __setstate__(self, d):
        self.__dict__.update(d)

    def get(self, request):
        timeoutValue = 30 #Maximum runtime for a job
        ttlValue = 60 #Maximum time a job can be enqueued
        logger = getLogger(__name__)
        config = ConfigReader()
        numqueues = config.get('saturnring','numqueues')
        allhosts=StorageHost.objects.all()
        jobs = {}
        rtnStr = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        for eachhost in allhosts:
            queuename = 'queue'+str(hash(eachhost)%int(numqueues))
            queue = get_queue(queuename)
            jobs[str(eachhost)]=queue.enqueue(UpdateOneState,args=(eachhost.dnsname,), timeout=timeoutValue,ttl=ttlValue)
        for eachhost in allhosts:
            while( jobs[str(eachhost)].is_queued or jobs[str(eachhost)].is_started):
                sleep(0.5)
        rtnStr = rtnStr + " ||| <hostname> : Host enabled boolean : Update returns (0 is good) : Job failed (False is good) "
        for eachhost in allhosts:
            rtnStr = rtnStr + "|||" + " : ".join([str(eachhost),str(eachhost.enabled),str(jobs[str(eachhost)].result),str(jobs[str(eachhost)].is_failed)])
        logger.info("Updatestate status: %s " %(rtnStr,))
        return Response(config.get('saturnring','clustername')+" state at "+rtnStr)

class Delete(APIView):
    """
    Delete a target, all targets on a saturn server, or all targets corresponding to
    a specific initiator
    /api/delete
    """
    def __getstate__(self):
        d = dict(self.__dict__)
        del d['logger']
        return d

    def __setstate__(self, d):
        self.__dict__.update(d)
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    def get(self, request ):
        logger = getLogger(__name__)
        logger.info("Raw request data is "+str(request.data))
        (flag,statusStr) = DeleteTarget(request.data,request.user)
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
    /api/provisioner
    """
    def __getstate__(self):
        d = dict(self.__dict__)
        del d['logger']
        return d

    def __setstate__(self, d):
        self.__dict__.update(d)
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    def get(self, request ):
        logger = getLogger(__name__)
        logger.info("Raw request data is "+str(request.data))
        serializer = ProvisionerSerializer(data=request.data)
        rtnDict = {}
        if serializer.is_valid():
            (flag,statusStr) = MakeTarget(request.data,request.user)
            if flag==-1:
                rtnDict = {}
                rtnDict['error']=1
                rtnDict['detail']=statusStr
                return Response(rtnDict, status=status.HTTP_400_BAD_REQUEST)
            if (flag==0 or flag==1):
                tar = Target.objects.filter(iqntar=statusStr)
                if (tar[0].owner != request.user):
                    return Response({'error':1,'detail':'Not authorized'},status=status.HTTP_401_UNAUTHORIZED)
                
                #if (flag != 1): #Dont run this code if this is a pre-existing LUN
                    #Check and update state on the Saturn node
                config = ConfigReader()
                numqueues = config.get('saturnring','numqueues')
                queuename = 'queue'+str(hash(tar[0].targethost)%int(numqueues))
                queue = get_queue(queuename)
                job = queue.enqueue(UpdateOneState,args=(tar[0].targethost.dnsname,), timeout=45,ttl=60)
                while not ( (job.result == 0) or (job.result == 1) or job.is_failed):
                    sleep(0.5)
                if (job.result == 1) or (job.is_failed):
                    rtnDict['error'] = 1
                    rtnDict['detail'] = "Saturn server %s on which the target %s is provisioned is not healthy/responding, contact admin" %(tar[0].targethost,tar[0].iqntar)
                    logger.error("Error while provisioning/returning target %s" %(tar[0].iqntar,))
                    return Response(rtnDict, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                data = tar.values('iqnini','iqntar','sizeinGB','targethost','storageip1','storageip2','aagroup__name','clumpgroup__name','sessionup','isencrypted','pin')
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
            logger.warn("Invalid provisioner serializer data: "+str(request.data))
            rtnDict={}
            rtnDict['error']=1
            rtnDict['detail']=serializer.errors
            return Response(rtnDict, status=status.HTTP_400_BAD_REQUEST)


class VGScanner(APIView):
    """
    Create or update models for all VGs on a Saturn server
    /api/vgscanner
    """
    def __getstate__(self):
        d = dict(self.__dict__)
        del d['logger']
        return d

    def __setstate__(self, d):
        self.__dict__.update(d)
    def get(self, request):
        logger = getLogger(__name__)
        logger.info("VG scan request received: %s " %(request.data,))
        saturnserver=request.data[u'saturnserver']
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
            logger.warn("Unknown saturn server "+str(request.data))
            return Response("Unregistered or uknown Saturn server "+str(request.data), status=status.HTTP_400_BAD_REQUEST)


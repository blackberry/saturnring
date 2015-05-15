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

from logging import getLogger
from ssdfrontend.models import LV
from ssdfrontend.models import VG
from ssdfrontend.models import StorageHost
from globalstatemanager.gsm import PollServer
from traceback import format_exc
from django.db import connection

#def UpdateState():
#    allvgs=VG.objects.all()
#    for eachvg in allvgs:
#        p = PollServer(eachvg.vghost)
#        p.GetVG()
#        p.UpdateLVs(eachvg)


#def UpdateState():
#    allhosts=StorageHost.objects.filter(enabled=True)
#    for eachhost in allhosts:
#        p = PollServer(eachhost)
#        vguuidList = p.GetVG()
#        logger.info("getvg returns "+str(vguuidList))
#        if type(vguuidList) is str:
#            for vguuid in vguuidList.split(','):
#                p.UpdateLVs(VG.objects.get(vguuid=vguuid))
#        p.GetTargetsState()
#        p.GetInterfaces()

def UpdateOneState(host):
    logger = getLogger(__name__)
    try:
        p = PollServer(host)
        vguuidList = p.GetVG()
        logger.info("getvg returns "+str(vguuidList))
        if type(vguuidList) is str:
            for vguuid in vguuidList.split(','):
                try:
                    vg = VG.objects.get(vguuid=vguuid)
                    p.UpdateLVs(vg)
                except:
                    logger.error("Cannot work with VG %s on %s" %(vguuid,host))
                    logger.error(format_exc())
        p.GetTargetsState()
        p.GetInterfaces()
    except:
        logger.error("UpdateOneState failed for %s " %(str(host),))
    finally:
        connection.close()



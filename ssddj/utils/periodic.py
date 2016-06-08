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
import logging
import logging.handlers
from ssdfrontend.models import LV
from ssdfrontend.models import VG
from ssdfrontend.models import StorageHost
from globalstatemanager.gsm import PollServer
from traceback import format_exc
from django.db import connection

def UpdateOneState(host):
    logger = logging.getLogger(__name__)
    socketHandler = logging.handlers.SocketHandler('localhost',
                    logging.handlers.DEFAULT_TCP_LOGGING_PORT)
    logger.addHandler(socketHandler)
    rtnVal = 0
    try:
        p = PollServer(host)
        checkServer = p.CheckServer()
        if checkServer != 0:
            rtnVal= -2
            raise Exception(str(host),checkServer)
        vguuidList = p.GetVG()
        if vguuidList == -1:
            rtnVal = -1
            raise Exception(str(host),"GetVG failed with -1 return value")
        logger.info("getvg returns "+str(vguuidList))
        if type(vguuidList) is str:
            for vguuid in vguuidList.split(','):
                try:
                    vg = VG.objects.get(vguuid=vguuid)
                    p.UpdateLVs(vg)
                except:
                    rtnVal = -1
                    logger.error(format_exc())
                    logger.error("Cannot work with VG %s on %s" %(vguuid,str(host)))
                    logger.error(format_exc())
        tarState = p.GetTargetsState()
        if tarState == -1:
            rtnVal = -1
            raise Exception(str(host),"Target state read error")
        interfaceRtn = p.GetInterfaces()
        if interfaceRtn == -1:
            rtnVal = -1
            raise Exception(str(host),"Interface scan error")
    except:
        logger.error(format_exc())
        logger.error("UpdateOneState failed for %s " %(str(host),))

    finally:
        try:
            sh = StorageHost.objects.get(dnsname=str(host))
            if (rtnVal == -2) and (sh.enabled == True):
                #sh.enabled = False
                #sh.save()
                logger.critical("Saturn server %s is in error (checkserver script run failed), please fix it or disable it." %(str(host),))
            if (rtnVal == -1):
                logger.error("Error in UpdateOneState (check outputs of vgs,lvs on %s: specifics: %s " %(str(host), format_exc()))
        except:
            logger.error("Error reading storage host %s information from DB in UpdateOneState" %(str(host),))
            logger.error(format_exc())
    connection.close()
    return rtnVal


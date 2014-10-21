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

from ssdfrontend.models import LV
from ssdfrontend.models import VG
from ssdfrontend.models import StorageHost
from globalstatemanager.gsm import PollServer


#def UpdateState():
#    allvgs=VG.objects.all()
#    for eachvg in allvgs:
#        p = PollServer(eachvg.vghost)
#        p.GetVG()
#        p.UpdateLVs(eachvg)


def UpdateState():
    allhosts=StorageHost.objects.filter(enabled=True)
    for eachhost in allhosts:
        p = PollServer(eachhost)
        vguuidList = p.GetVG()
        if vguuidList <> -1:
            for vguuid in vguuidList:
                p.UpdateLVs(VG.objects.get(vguuid=vguuid))
        p.GetTargetsState()
        p.GetInterfaces()

def UpdateOneState(host):
    p = PollServer(host)
    vguuidList = p.GetVG()
    if vguuidList <> -1:
        for vguuid in vguuidList:
            p.UpdateLVs(VG.objects.get(vguuid=vguuid))
    p.GetTargetsState()
    p.GetInterfaces()

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
        vguuid = p.GetVG()
        if vguuid <> -1:
            p.UpdateLVs(VG.objects.get(vguuid=vguuid))


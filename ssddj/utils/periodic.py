from ssdfrontend.models import LV
from ssdfrontend.models import VG
from globalstatemanager.gsm import PollServer


def UpdateState():
    allvgs=VG.objects.all()
    for eachvg in allvgs:
        p = PollServer(eachvg.vghost)
        p.GetVG()
        p.UpdateLVs(eachvg)



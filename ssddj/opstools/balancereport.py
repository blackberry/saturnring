import os
import sys
from traceback import format_exc
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ssddj.settings")
from django.conf import settings

from ssdfrontend.models import Target
from ssdfrontend.models import LV
from ssdfrontend.models import VG
from ssdfrontend.models import AAGroup
from ssdfrontend.models import StorageHost
from ssdfrontend.models import User 


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

#username = sys.argv[1]
#owner = User.objects.get(username=username);
allTargets = Target.objects.all()
vgdic = {}
aagdic = {}
shostdic = {}
#print bcolors.BOLD + "\n\nUsers' target information" + bcolors.ENDC
for aTarget in allTargets:
  try:
    lv = LV.objects.get(target=aTarget)
    vg = lv.vg
    aag = AAGroup.objects.get(target=aTarget)
    owner = aTarget.owner
    print owner.username,
    print bcolors.OKGREEN + aTarget.iqntar + bcolors.ENDC,
    print aTarget.iqnini,
    print str(aTarget.created_at),
    print bcolors.OKBLUE + vg.vghost.dnsname +bcolors.ENDC,
    print vg.vguuid,
    print lv.lvname,
    print str(aag)
    aag = str(aag)
    if str(vg) not in vgdic:
        vgdic[str(vg)] = []
    vgdic[str(vg)].append((str(aTarget),aTarget.iqnini,owner.username))
    
    if aag not in aagdic:
        aagdic[aag] = []
    aagdic[aag].append((str(aTarget),aTarget.iqnini,owner.username))
    
    shost = aTarget.targethost.dnsname
    if shost not in shostdic:
        shostdic[shost] = {}
    if aag not in shostdic[shost]:
        shostdic[shost][aag] = []
    shostdic[shost][aag].append((str(aTarget),aTarget.iqnini,owner.username))
  except:
    print "Error processing %s" % str(aTarget)
    print format_exc()


print bcolors.BOLD + "\n\nUsers' targets per VG" +bcolors.ENDC
for vg in sorted(vgdic.keys()):
    print bcolors.OKGREEN + vg + bcolors.ENDC
    for atarget in vgdic[vg]:
	(targetname, initiatorname,username) = atarget
        print bcolors.OKGREEN + username + bcolors.ENDC,
        print bcolors.OKBLUE + targetname + bcolors.ENDC,
        print initiatorname

print bcolors.BOLD + "\n\nAAG targets per Saturn Server" +bcolors.ENDC
print "Anti_affinity_group Username Target_IQN Initiator_client_IQN Overlap"
for shost in sorted(shostdic.keys()):
    for aag in shostdic[shost]:
        overlapsize = len(shostdic[shost][aag])
        if overlapsize > 1:
            for eachTarget in shostdic[shost][aag]:
                (targetname, initiatorname,username) = eachTarget
                print bcolors.OKBLUE + aag + bcolors.ENDC,
                print bcolors.FAIL + username + bcolors.ENDC,
                print bcolors.WARNING + targetname + bcolors.ENDC,
                print bcolors.FAIL + initiatorname +" "+ str(overlapsize) + bcolors.ENDC




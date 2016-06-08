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

#migratetarget.py

from traceback import format_exc
import sys, os, hashlib
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ssddj.settings")
from django.conf import settings
import django
django.setup()
try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
except ImportError:
    from django.contrib.auth.models import User    

from operator import itemgetter
from ssdfrontend.models import Target,LV,VG,StorageHost,AAGroup, Interface, ClumpGroup, IPRange
from globalstatemanager.gsm import PollServer
from utils.targetops import ExecMakeTarget

def LVAllocSumVG(vg):
    '''
    Simple function to return sum of LV sizes in a specified VG
    '''
    lvs = LV.objects.filter(vg=vg)
    lvalloc=0.0
    for eachlv in lvs:
       lvalloc=lvalloc+eachlv.lvsize
    return lvalloc

def VGFilterChoices(storageSize, aagroup,owner,clumpgroup="noclump",subnet="public",storemedia='randommedia',provisiontype='any'):
    '''
    The key filtering and "anti-affinity logic" function
    Check if StorageHost is enabled
    Check if VG is enabled
    Find all VGs where SUM(Alloc_LVs) + storageSize < totalGB
    Return a random choice from these
    Or do AAG logic
    '''
    storagehosts = StorageHost.objects.filter(enabled=True)
    qualvgs = []
    if storemedia=='randommedia':
        if provisiontype != 'any':
            vgchoices = VG.objects.filter(in_error=False,is_locked=False,vghost__in=storagehosts,enabled=True,is_thin=provisiontype).order_by('-maxavlGB')#Ordering for randomaag going to least used VG
        else:
            vgchoices = VG.objects.filter(in_error=False,is_locked=False,vghost__in=storagehosts,enabled=True).order_by('-maxavlGB')#Ordering for randomaag going to least used VG
    else:
        if provisiontype != 'any':
            vgchoices = VG.objects.filter(in_error=False,is_locked=False,vghost__in=storagehosts,enabled=True,storemedia=storemedia,is_thin=provisiontype).order_by('-maxavlGB')#randomaag goes to least used VG
        else:
            vgchoices = VG.objects.filter(in_error=False,is_locked=False,vghost__in=storagehosts,enabled=True,storemedia=storemedia).order_by('-maxavlGB')#randomaag goes to least used VG

    if len(vgchoices) > 0:
        numDel=0
        chosenVG = -1
        for eachvg in vgchoices:
            if subnet != "public":
                try:
                    eachvg.vghost.iprange_set.get(iprange=subnet,owner=owner)
                except:
                    var = format_exc()
                    continue

            lvalloc = LVAllocSumVG(eachvg)
            eachvg.CurrentAllocGB=lvalloc
            eachvg.save()
            if (lvalloc + float(storageSize)) > (eachvg.totalGB):
               numDel=numDel+1
            else:
                if clumpgroup=="noclump":
                    if aagroup=="random":
                        #return eachvg
                        qualvgs.append((eachvg,0,eachvg.maxavlGB))
                    else:
                        qualvgs.append((eachvg,eachvg.vghost.aagroup_set.all().filter(name=aagroup).count(),eachvg.maxavlGB))
                else:
                    qualvgs.append((eachvg,eachvg.vghost.clumpgroup_set.all().filter(name=clumpgroup).count(),eachvg.maxavlGB))
        if ((aagroup=="random") and (clumpgroup=="noclump")):
            return sorted(qualvgs,key=itemgetter(2),reverse=True);

        if ( len(qualvgs) > 0 ) and (clumpgroup != "noclump"):
            s = sorted(qualvgs,key=itemgetter(2),reverse=True) #Secondary sort, descending avl space in VG, using sort stability 
            chosenVG,overlap,maxvg = sorted(s, key=itemgetter(1))[-1] #Primary sort, chose host with maximum clump peers, using sort stability
            if overlap == 0:
                for ii in range(0,len(qualvgs)): #There is no clump peer, so need to fall back to aagroup
                    (vg,discardthis,maxvg) = qualvgs[ii]
                    qualvgs[ii]= (vg,vg.vghost.aagroup_set.all().filter(name=aagroup).count(),maxvg)
            else:
                return sorted(s, key=itemgetter(1))

        if len(qualvgs) > 0:
            s = sorted(qualvgs,key=itemgetter(2),reverse=True) #Secondary sort
            chosenVG,overlap,maxvg =sorted(s, key=itemgetter(1))[0] #Primary sory
            return sorted(s, key=itemgetter(1))
        if len(vgchoices)>numDel:
            return sorted(s, key=itemgetter(1))
        else:
            return -1
    else:
        return -1
    return -1

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def GenerateTargetName(clientiqn,targetHost,serviceName):
    clientiqnHash = hashlib.sha1(clientiqn).hexdigest()[:8]
    iqnTarget = "".join(["iqn.2014.01.",str(targetHost),":",serviceName,":",clientiqnHash])
    return iqnTarget

#DB entries and input sanity check
def query_yes_no(question, default="no"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)
    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")

def AutoSuggest(tarobj,fromvgobj,aagobj):
    if (tarobj.storageip1 != fromvgobj.vghost.storageip1):
        subnet = Interface.objects.get(ip=tarobj.storageip1,storagehost=from_vg.vghost).iprange.all()[0].iprange
    else:
        subnet = "public"
    cg = ClumpGroup.objects.get(target=from_tar)
    tuplelist = VGFilterChoices(tarobj.sizeinGB,aagobj.name,tarobj.owner,cg.name,subnet)
    if (tuplelist == -1):
        print "Error finding a suitable destination match"
        sys.exit()
    else:
        print ("Short listed %d possibilities (sorted most desirable to lesser desirable), select one" %len(tuplelist))
        for item in tuplelist:

            (vg,overlap,maxavl) = item
            if (fromvgobj.vghost == vg.vghost):
                print "Skipping vg %s because it is on the same saturn server as %s is on currently" %(vg,tarobj.iqntar)
                continue
            if (query_yes_no(str(vg),default="yes")):
                return vg
    print "No option selected"
    sys.exit()

#########################
#Main script starts here#
#########################

print bcolors.BOLD + "Usage: python migratetarget.py <target-iqn> <auto|destination_VG_uuid> <saturnbox linux username>" + bcolors.ENDC

try:
    from_tar = Target.objects.get(iqntar=sys.argv[1])
    from_lv = LV.objects.get(target=from_tar)
    from_vg = from_lv.vg
    aag = AAGroup.objects.get(target=from_tar)
    if (sys.argv[2] == "auto"):
        to_vg = AutoSuggest(from_tar,from_vg,aag)
    else:
        to_vg = VG.objects.get(vguuid=sys.argv[2])

    linuxusername = sys.argv[3]
    destserver = PollServer(to_vg.vghost.dnsname)
    sourceserver = PollServer(from_vg.vghost.dnsname)
except:
    print bcolors.FAIL + format_exc() + bcolors.ENDC
    sys.exit()

print bcolors.BOLD+ "From_target: %s " %(from_tar,) + bcolors.ENDC
print bcolors.OKGREEN + "From_vg: %s "%(from_vg,) + bcolors.ENDC
print bcolors.OKGREEN + "From_lv: %s "%(from_lv,) + bcolors.ENDC
print bcolors.OKGREEN + "To_vg: %s "%(to_vg,) + bcolors.ENDC
print bcolors.OKGREEN + "Anti-affinity-group: %s "%(aag,) + bcolors.ENDC


#Same VG specified check
if str(from_vg) == str(to_vg):
    print bcolors.FAIL + "Target %s on VG %s cannot be moved to the *same* VG %s specified on the command line! " %(from_tar.iqntar,from_vg,to_vg) + bcolors.ENDC
    sys.exit()

#Same StorageHost specified check
if (from_vg.vghost.dnsname == to_vg.vghost.dnsname):
    print bcolors.FAIL + "Intra-host migration not supported (source and destination VGs must be on different hosts)" + bcolors.ENDC
    sys.exit()


#iSCSI Session down check
if from_tar.sessionup:
    print bcolors.FAIL + "Target %s DB entry reports session up, please bring down the session in the DB." %(from_tar,) + bcolors.ENDC
    sys.exit()
else:
    print bcolors.FAIL + "Appears iSCSI session is down on target %s, proceeding" %(from_tar,) + bcolors.ENDC

#Capacity check
if to_vg.maxavlGB < from_tar.sizeinGB:
    print bcolors.FAIL + "Specified target VG %s does not have adequate space for specified target %s (%d GB < %d GB) " %(str(to_vg),str(from_tar),to_vg.maxavlGB,from_tar.sizeinGB) + bcolors.ENDC
    sys.exit()
else:
    print bcolors.OKGREEN + "Passed capacity check" + bcolors.ENDC

#Anti-affinity check
oldoverlap = from_lv.vg.vghost.aagroup_set.all().filter(name=aag).count()
newoverlap = to_vg.vghost.aagroup_set.all().filter(name=aag).count() + 1
print bcolors.OKBLUE + "Old VG's anti-affinity overlap = %d " %(oldoverlap,) + bcolors.ENDC
print bcolors.OKBLUE + "New VG's anti-affinity overlap = %d " %(newoverlap,) + bcolors.ENDC

if (oldoverlap < newoverlap):
    print bcolors.FAIL + "Greater anti-affinity overlap may be detrimental to the LUNs' High availability." + bcolors.ENDC
    if (query_yes_no("Sure ?") == False):
        sys.exit()
else:
    print bcolors.OKGREEN + "Anti-affinity is not worsened, so passed." + bcolors.ENDC


#Generate new target iqn name
serviceName = from_tar.iqntar.split(':')[1]
to_tar = GenerateTargetName(from_tar.iqnini,to_vg.vghost.dnsname,serviceName)
try:
    Target.objects.get(iqntar=to_tar)
    print bcolors.FAIL + "Generated target name %s already exists, cannot migrate to this destination host (try another host). " %(to_tar,) + bcolors.ENDC
    sys.exit()
except:
    print bcolors.BOLD + "New target name will be %s" %(to_tar,) + bcolors.ENDC



# Check that session is down on source server (if not already down)
cmdStr = " ".join(["sudo",sourceserver.rempypath, os.path.join(sourceserver.remoteinstallLoc,'saturn-bashscripts','parsetarget.py'), '2> parsetargeterror.txt'])
exStr = sourceserver.Exec(cmdStr)
for aLine in exStr:
    if from_tar.iqntar in aLine:
        if "no sessions" not in aLine:
            print bcolors.FAIL + "Session is up on host %d for target %d, please bring it down before running the migration" %(sourceserver.serverDNS,from_tar.iqntar) + bcolors.ENDC
            sys.exit()
        else:
            break

# Check if the required IPRange is available at the destination server
to_subnet = "public"
storeip1 = "notdefined"
try:
    if (from_tar.storageip1 != from_vg.vghost.storageip1): #Meaning a subnet was specified:
        subnet = Interface.objects.get(ip=from_tar.storageip1,storagehost=from_vg.vghost).iprange.all()[0]
        storeip1 = Interface.objects.get(owner=from_tar.owner,storagehost=to_vg.vghost,iprange__iprange=unicode(subnet)).ip
        to_subnet = subnet.iprange
    else:
        storeip1 = to_vg.vghost.storageip1
    print bcolors.OKBLUE + "Using subnet "+to_subnet + bcolors.ENDC
    print bcolors.OKBLUE + "Using interface on destination server "+storeip1 + bcolors.ENDC
except:
    print bcolors.FAIL + "Subnet issue" + bcolors.ENDC
    print bcolors.FAIL + format_exc() + bcolors.ENDC
    sys.exit()

# Create LV on destination server/VG
cmdStr = " ".join(["sudo vgdisplay -c | grep ",to_vg.vguuid,"| cut -d: -f1"])
to_vgname = destserver.Exec(cmdStr)[0].strip()
#cmdStr = " ".join(["sudo lvcreate" ,to_vgname, "-L", str(from_tar.sizeinGB)+"G", "-n", to_lvname])
#print bcolors.FAIL + destserver.Exec(cmdStr)[0].strip() + bcolors.ENDC

#From_vg name
cmdStr = " ".join(["sudo vgdisplay -c | grep ",from_vg.vguuid,"| cut -d: -f1"])
from_vgname = sourceserver.Exec(cmdStr)[0].strip()
to_lvname = 'lvol-'+hashlib.md5(to_tar+'\n').hexdigest()[0:8]

# Disabling old iSCSI target on source host
# Example
# sudo sh -c 'echo 0 >  /sys/kernel/scst_tgt/targets/iscsi/iqn.2014.01.192.168.50.51:whatever2:aa52c708/enabled'
cmdStr = "sudo sh -c " + "'echo 0 > /sys/kernel/scst_tgt/targets/iscsi/"+from_tar.iqntar+"/enabled'"
for aLine in sourceserver.Exec(cmdStr):
    print bcolors.OKBLUE + aLine + bcolors.ENDC

#Delete DB entry for the old target and the old LV
to_iqnini = from_tar.iqnini
to_sizeinGB = from_tar.sizeinGB
to_aagname = aag.name

cg = ClumpGroup.objects.get(target=from_tar)
to_cgname = cg.name
to_owner = from_tar.owner.username
to_isencrypted = str(int(from_tar.isencrypted))
from_tarname = from_tar.iqntar
from_lvname = from_lv.lvname
from_lvuuid = from_lv.lvuuid
from_created_at = from_lv.created_at
from_updated_at = from_lv.updated_at
from_isencrypted = from_lv.isencrypted
from_storageip1 = from_tar.storageip1
from_storageip2 = from_tar.storageip2
from_lv.delete()
from_tar.delete()

# Creating new target on the destination 

ExecMakeTarget(to_vg.storemedia,to_vg.vguuid,destserver.serverDNS,to_iqnini,
        serviceName,to_sizeinGB,to_aagname,to_cgname,to_subnet,to_owner,to_isencrypted)

#Actual copy:

#Copy over ssh key for password-less login from source to destination:
print "Copying SSH key..."
sshkey = sourceserver.PutKeyFile('saturnkey')
cmdStr = str(" ".join(['sudo chmod 600 ',sshkey]))
print str(sourceserver.Exec(cmdStr))

if int(to_isencrypted): # dd-copy the encrypted volume to encrypted volume
    source = str("".join(["/dev/mapper/encrypted_",str(from_lvname)]))
    destination = str("".join(["/dev/mapper/encrypted_",str(to_lvname)]))
else: # dd-copy the plain volume to plain volume
    source = str("".join(['/dev/',str(from_vgname),'/',str(from_lvname)]))
    destination = str("".join(['/dev/',str(to_vgname),'/',str(to_lvname)]))

#If you need compression add a -C flag to ssh    
cmdStr = str(" ".join(['sudo dd if='+source, ' bs=1M',' | ssh ',
    ' -o UserKnownHostsFile=/dev/null',
    ' -o StrictHostKeyChecking=no',
    ' -i ',sshkey, linuxusername+'@'+str(destserver.serverDNS),' sudo dd of='+destination,' bs=1M']))
print bcolors.OKBLUE + "Copy command: "+ cmdStr + bcolors.ENDC
print bcolors.WARNING + "Starting copy... (check progress via watch ifconfig <net-dev> although compression is enabled, so empty LUNs will not register much network traffic.)... ... ..." + bcolors.ENDC
#outStr = "Demo run"
outStr = sourceserver.Exec(cmdStr)
print bcolors.OKBLUE + str(outStr)  + bcolors.ENDC

if(query_yes_no("ROLLBACK? Do you want to roll back?")):
    try:
        new_lv_to_del = LV.objects.get(lvname=to_lvname).delete()
        new_tar_to_del = Target.objects.get(iqntar=to_tar).delete()
    except:
        print bcolors.FAIL + format_exc() + bcolors.ENDC
    try:
        owner = User.objects.get(username=to_owner)
        restore_old_tar = Target(owner=owner,targethost=from_vg.vghost,iqnini=to_iqnini,
                iqntar=from_tarname,sizeinGB=to_sizeinGB,storageip1=from_storageip1,
                storageip2=from_storageip2,isencrypted=from_isencrypted)
        restore_old_tar.save()
        #LV
        restore_old_lv = LV(target=restore_old_tar,lvname=from_lvname,lvsize=to_sizeinGB,
                vg=from_vg,lvuuid=from_lvuuid,isencrypted=from_isencrypted)
        restore_old_lv.save()
        #AAG
        restore_old_aag = AAGroup(name=to_aagname,target=restore_old_tar)
        restore_old_aag.save()
        restore_old_aag.hosts.add(restore_old_tar.targethost)
        restore_old_aag.save()
        restore_old_tar.aagroup=restore_old_aag

        restore_old_cg = ClumpGroup(name=to_cgname,target=restore_old_tar)
        restore_old_cg.save()
        restore_old_cg.hosts.add(restore_old_tar.targethost)
        restore_old_cg.save()
        restore_old_tar.clumpgroup=restore_old_cg
        restore_old_tar.save()

        print bcolors.OKGREEN + "To remove any newly provisioned storage run this sequence of commands:" + bcolors.ENDC
        print "1. Log into the iSCSI server "
        print bcolors.BOLD + "ssh local@"+destserver.serverDNS + bcolors.ENDC
        print "2. Navigate to the Saturn scripts directory" 
        print bcolors.BOLD + "cd "+os.path.join(destserver.remoteinstallLoc,'saturn-bashscripts') + bcolors.ENDC
        print "3. To reclaim any provisioned storage, run the Deletetarget script"
        print bcolors.BOLD + "sudo ./removetarget.sh "+to_tar+ " "+ to_vg.vguuid +" " + to_lvname + bcolors.ENDC
        sys.exit()
    except SystemExit:
        print "Exiting normally."
        sys.exit()
    except:
        print bcolors.FAIL + format_exc() + bcolors.ENDC
        sys.exit()

if(query_yes_no("Do you want to make the changes permanent (reclaim old storage)?")):
    try:
        print str(sourceserver.Exec(" ".join(["sudo",os.path.join(sourceserver.remoteinstallLoc,'saturn-bashscripts','removetarget.sh'), sys.argv[1], from_vg.vguuid, from_lvname])))
    except:
        print format_exc()
else:
    print bcolors.OKGREEN + "To permanantly remove the old storage LV and target:" + bcolors.ENDC
    print "1. Log into the iSCSI server of the old target:"
    print bcolors.BOLD + "ssh local@"+sourceserver.serverDNS + bcolors.ENDC
    print "2. Navigate to the Saturn scripts directory" 
    print bcolors.BOLD + "cd "+os.path.join(sourceserver.remoteinstallLoc,'saturn-bashscripts') + bcolors.ENDC
    print "3. To reclaim old storage, run the Deletetarget script"
    print bcolors.BOLD + "sudo ./removetarget.sh "+sys.argv[1]+ " "+ from_vg.vguuid +" " + from_lvname + bcolors.ENDC









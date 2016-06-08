import os
import logging
from logging import getLogger
import ConfigParser
from utils.targetops import DeleteTargetObject
from django import forms
from django.contrib import messages
from ssdfrontend.models import GenerateRandomPin
from admin_stats.admin import StatsAdmin, Avg, Sum
from ssdfrontend.models import Profile, Target, VG, LV
from traceback import format_exc
from django import db
import django_rq
import time

def delete_selected_iscsi_targets(StatsAdmin,request,queryset):
    logger = logging.getLogger(__name__)
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    config = ConfigParser.RawConfigParser()
    config.read(os.path.join(BASE_DIR,'saturn.ini'))
    numqueues = config.get('saturnring','numqueues')
    jobs =[]
    for obj in queryset:
        queuename = 'queue'+str(hash(obj.targethost)%int(numqueues))
        queue = django_rq.get_queue(queuename)
        jobs = []
        jobs.append( (queue.enqueue(DeleteTargetObject,args=(obj.iqntar,),timeout=45), obj.iqntar) )
        logger.info("Using queue %s for deletion" %(queuename,))
    rtnStatus= {}
    rtnFlag=0
    numDone=0
    timeCtr=0
    while (numDone < len(jobs)) and (timeCtr < 120):
        ii=0
        timeCtr=timeCtr+1
        time.sleep(0.5)
        for ii in range(0,len(jobs)):
            if jobs[ii] == 0:
                continue
            (job,target) = jobs[ii]
            if (job.result == 0) or (job.result == 1):
                if job.result==1:
                    try:
                        logger.error('Failed deletion of '+target)
                        raise forms.ValidationError(
                            ('Failed deletion target: %(target)'),
                            code='invalid', 
                            params={'values': 'Check if session is up'},
                        )
                    except:
                        rtnStatus[target]="Error deleting %s: %s" %(obj.iqntar,str(job.result))
                        messages.error(request,"Error deleting %s : %s " %(obj.iqntar,format_exc()))
                else:
                    messages.success(request,'Deleted %s' %obj.iqntar)

                rtnFlag=rtnFlag + job.result
                jobs[ii]=0
                numDone=numDone+1
            else:
                logger.info('...Working on deleting target '+target)
                break
    if timeCtr == 120:
        logger.error("Gave up trying to delete after 1 minute")
    return (rtnFlag,str(rtnStatus))



def set_identical_pin_for_all_selected_targets(StatsAdmin,request,queryset):
    logger = logging.getLogger(__name__)
    randompin = GenerateRandomPin()
    for obj in queryset:
        obj.pin = randompin
        obj.save()


def config_snapshots(StatsAdmin,request,queryset):
    targetList = []
    for obj in queryset:
        targetList.append(obj.iqntar)
    return redirect('snapbackup:snapconfig',targets=obj)
#    return redirect('snapconfig')


def Physical_Location(obj):
    mylv = LV.objects.get(target=obj)
    return str(mylv.vg) + ":LV:"+str(mylv)

def download_selected_targets_to_CSV(StatsAdmin,request,queryset):
    from djqscsv import render_to_csv_response
    qs = queryset.values('owner__username','iqntar','iqnini','sizeinGB','targethost','lv__vg','lv__lvname')

    return render_to_csv_response(qs, field_header_map={'targethost':'Saturnserver_name','lv__lvname':'LV_name','lv__vg':'VG_name','owner__username':'Owner'})
    

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = '__all__'
    
    def clean_max_alloc_sizeGB(self):
        logger = getLogger(__name__)
        oldalloc = 0
        usedsize = 0
        #Test 1:  if the user has already used more than the new quota
        try:
            requestedGB = self.cleaned_data['max_alloc_sizeGB']
            usedsize = Target.objects.filter(owner=self.cleaned_data['user']).aggregate(used_size=db.models.Sum('sizeinGB'))['used_size']
            if usedsize == None:
                usedsize = 0
            if (usedsize > requestedGB):
                raise forms.ValidationError("Sorry, user targets already using %d GB > new requested quota %d GB, perhaps the user should delete some iSCSI targets before asking for a lower quota." %(usedsize,requestedGB))
        except:
            logger.error(format_exc())
            raise forms.ValidationError("Sorry, user targets already using %d GB > new requested quota %d GB, perhaps the user should delete some iSCSI targets before asking for a lower quota." %(usedsize,requestedGB))
            logger.error("Sorry, user targets already using %d GB > new requested quota %d GB, perhaps the user should delete some iSCSI targets before asking for a lower quota." %(usedsize,requestedGB))

        #Test 2: if the cluster has that much available storage
        try:
            requestedGB = self.cleaned_data['max_alloc_sizeGB']
            if requestedGB == 0:
                return requestedGB
            totalGB = VG.objects.all().aggregate(totalGB=db.models.Sum('totalGB'))['totalGB']
            if totalGB == None:
                totalGB = 0
            allocGB = Profile.objects.all().aggregate(CAGB=db.models.Sum('max_alloc_sizeGB'))['CAGB']
            if allocGB == None:
                allocGB = 0
            thisuser = self.cleaned_data['user']
            try:
                oldalloc = Profile.objects.get(user=thisuser).max_alloc_sizeGB
            except:
                oldalloc = None
            if oldalloc == None:
                oldalloc = 0
            #logger.info("totalGB = %d, Allocated to all users = %d, This users old allocation = %d" %(totalGB,allocGB,oldalloc)) 
            if (totalGB < allocGB+requestedGB-oldalloc) and (requestedGB > oldalloc):
                raise forms.ValidationError("Sorry, cluster capacity exceeded; maximum possible is %d GB" %(totalGB-allocGB+oldalloc,))
        except:
            logger.error(format_exc())
            logger.error("Sorry, cluster capacity exceeded; maximum possible is %d GB" %(totalGB-allocGB+oldalloc,))
            raise forms.ValidationError("Sorry, cluster capacity exceeded; maximum possible is %d GB" %(totalGB-allocGB+oldalloc,))
        return requestedGB



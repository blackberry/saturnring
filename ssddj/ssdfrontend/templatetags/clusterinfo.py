from django import template

from ssdfrontend.models import StorageHost
from ssdfrontend.models import VG
from django.db.models import Sum
from django.db.models import Max 
from ssdfrontend.models import Profile
register = template.Library()

@register.simple_tag
def get_clusterinfo():
    try:
        numHosts = StorageHost.objects.all().count()
        if numHosts == None:
            numHosts = 0

        totalCap =  VG.objects.all().aggregate(totalGB=Sum('totalGB'))['totalGB']
        avlCap = VG.objects.all().aggregate(totalavl=Sum('maxavlGB'))['totalavl']
        maxSize = VG.objects.all().aggregate(maxLUN=Max('maxavlGB'))['maxLUN']
        quotapromised = Profile.objects.all().aggregate(totalquota=Sum('max_alloc_sizeGB'))['totalquota']
        if totalCap == None:
            totalCap = -9999999999
        if (avlCap == None) or (avlCap < 0):
            avlCap = -99999999999
        return "Saturn servers: %d; Total/quota-promised/in-actual-use/Max-LUN-size : %d/%d/%d/%d GB" %(numHosts,totalCap,quotapromised,totalCap-avlCap,maxSize)
    except:
        return 'Undefined'
        

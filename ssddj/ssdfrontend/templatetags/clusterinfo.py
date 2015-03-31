from django import template

from ssdfrontend.models import StorageHost
from ssdfrontend.models import VG
from django.db.models import Sum
from django.db.models import Max 
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
        if totalCap == None:
            totalCap = -9999999999
        if (avlCap == None) or (avlCap < 0):
            avlCap = -99999999999
        return "Saturn servers: %d; Total/Available/Max LUN capacity: %d/%d/%d GB" %(numHosts,totalCap,avlCap,maxSize)
    except:
        return 'Undefined'
        

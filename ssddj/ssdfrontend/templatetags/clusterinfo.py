from django import template

from ssdfrontend.models import StorageHost
from ssdfrontend.models import VG
from django.db.models import Sum
register = template.Library()

@register.simple_tag
def get_clusterinfo():
    try:
        numHosts = StorageHost.objects.all().count()
        if numHosts == None:
            numHosts = 0

        totalCap =  VG.objects.all().aggregate(totalGB=Sum('totalGB'))['totalGB']
        if totalCap == None:
            totalCap = 0
        return "%d saturn servers with total capacity  %d GB." %(numHosts,totalCap)
    except:
        return 'Undefined'
        

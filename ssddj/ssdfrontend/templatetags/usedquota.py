from django import template
from ssdfrontend.models import Target
from ssdfrontend.models import User 
from utils.configreader import ConfigReader
from django.db.models import Sum
register = template.Library()

@register.simple_tag
def get_usedquota(theuser):
    user = User.objects.get(username=theuser)
    usedsize = Target.objects.filter(owner=user).aggregate(Sum('sizeinGB'))
    numtargets = Target.objects.filter(owner=user).count()
    if 'None' in str(usedsize):
        usedsize = 0
    return str(usedsize) + ' GB across ' + str(numtargets) + ' targets'

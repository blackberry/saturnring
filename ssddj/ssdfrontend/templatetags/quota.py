from django import template
from ssdfrontend.models import Target
from ssdfrontend.models import user 
from utils.configreader import ConfigReader

register = template.Library()

@register.simple_tag
def get_quota(theuser):
    totalalloc = Target.objects.filter(owner=owner).aggregate(Sum('sizeinGB'))
    user = User.objects.get(username=theuser)
    largesttarget = user.profile.max_target_sizeGB
    totalquota = user.profile.max_alloc_sizeGB


from django.template import Library
from ssdfrontend.models import Target
from utils.configreader import ConfigReader

register = Library()

@register.simple_tag
def get_quota(theuser):
    try:
        from ssdfrontend.models import user 
        totalalloc = Target.objects.filter(owner=owner).aggregate(Sum('sizeinGB'))
        user = User.objects.get(username=theuser)
        largesttarget = user.profile.max_target_sizeGB
        totalquota = user.profile.max_alloc_sizeGB
    except:
        totalalloc = "Not defined"
        largesttarget = "Not defined"
        totalquota = "Not defined"


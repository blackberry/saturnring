from django import template
from ssdfrontend.models import Target
from ssdfrontend.models import User 
from utils.configreader import ConfigReader

register = template.Library()

@register.simple_tag
def get_maxlunsize(theuser):
    user = User.objects.get(username=theuser)
    return str(user.profile.max_target_sizeGB) + ' GB'


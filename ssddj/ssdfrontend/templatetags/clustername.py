from django import template

from utils.configreader import ConfigReader

register = template.Library()

@register.simple_tag
def get_clustername():
    config = ConfigReader()
    return config.get('saturnring','clustername')

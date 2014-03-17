from django.contrib import admin

from ssdfrontend.models import Target 
from ssdfrontend.models import StorageHost
from ssdfrontend.models import LV 
from ssdfrontend.models import VG 
from ssdfrontend.models import Provisioner

admin.site.register(Target)
admin.site.register(StorageHost)
admin.site.register(LV)
admin.site.register(VG)
admin.site.register(Provisioner)
# Register your models here.

from django.contrib import admin

from ssdfrontend.models import Target 
from ssdfrontend.models import StorageHost
from ssdfrontend.models import LV 
from ssdfrontend.models import VG 
from ssdfrontend.models import Provisioner

admin.site.register(StorageHost)
admin.site.register(LV)
admin.site.register(VG)
# Register your models here.
from django.contrib import admin

from ssdfrontend.models import Target


class TargetAdmin(admin.ModelAdmin):
  def has_change_permission(self, request, obj=None):
        has_class_permission = super(TargetAdmin, self).has_change_permission(request, obj)
        if not has_class_permission:
            return False
        if obj is not None and not request.user.is_superuser and request.user.id != obj.owner.id:
            return False
        return True

  def queryset(self, request):
        if request.user.is_superuser:
            return Target.objects.all()
        return Target.objects.filter(owner=request.user)

  def save_model(self, request, obj, form, change):
        if not change:
            obj.owner = request.user
        obj.save()


admin.site.register(Provisioner)
admin.site.register(Target, TargetAdmin)

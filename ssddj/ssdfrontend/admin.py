from django.contrib import admin

from ssdfrontend.models import Target 
from ssdfrontend.models import StorageHost
from ssdfrontend.models import LV 
from ssdfrontend.models import VG 
from ssdfrontend.models import Provisioner

admin.site.register(StorageHost)
admin.site.register(VG)
# Register your models here.
#from django.contrib import admin
from admin_stats.admin import StatsAdmin, Avg, Sum

from ssdfrontend.models import Target




class TargetAdmin(StatsAdmin):
    readonly_fields = ('targethost','iqnini','iqntar','clienthost','sizeinGB','owner',)
    list_display = ['iqntar', 'iqnini','sizeinGB']
    stats = (Sum('sizeinGB'),)
    def has_delete_permission(self, request, obj=None): # note the obj=None
                return False
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


class LVAdmin(StatsAdmin):
    readonly_fields = ('target','vg','lvname','lvsize','lvuuid','lvthinmapped',)
    list_display = ['target', 'owner_name', 'lvsize','lvthinmapped']
    stats = (Sum('lvsize'),Sum('lvthinmapped'),)
    search_fields = ['target__iqntar','target__owner__username']
    def owner_name(self, instance):
                return instance.target.owner
    owner_name.admin_order_field  = 'target__owner'

    def has_delete_permission(self, request, obj=None): # note the obj=None
                return False
    def has_change_permission(self, request, obj=None):
        has_class_permission = super(LVAdmin, self).has_change_permission(request, obj)
        if not has_class_permission:
            return False
        if obj is not None and not request.user.is_superuser and request.user.id != obj.owner.id:
            return False
        return True

    def queryset(self, request):
        if request.user.is_superuser:
            return LV.objects.all()
        return LV.objects.filter(target__owner=request.user)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.owner = request.user
        obj.save()
admin.site.register(Provisioner)
admin.site.register(Target, TargetAdmin)
admin.site.register(LV,LVAdmin)

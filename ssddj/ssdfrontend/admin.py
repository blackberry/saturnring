from django.contrib import admin
from django import forms
from ssdfrontend.models import Target 
from ssdfrontend.models import StorageHost
from ssdfrontend.models import LV 
from ssdfrontend.models import VG 
from ssdfrontend.models import Provisioner
from ssdfrontend.models import AAGroup
#from ssdfrontend.models import HostGroup

from globalstatemanager.gsm import PollServer
#admin.site.register(StorageHost)
# Register your models here.
#from django.contrib import admin
from admin_stats.admin import StatsAdmin, Avg, Sum

import logging
logger = logging.getLogger(__name__)
admin.site.disable_action('delete_selected')
class VGAdmin(StatsAdmin):	
    readonly_fields = ('vghost','thintotalGB','maxthinavlGB','thinusedpercent','CurrentAllocGB')
    list_display = ['vghost','thintotalGB','maxthinavlGB','CurrentAllocGB','thinusedpercent','thinusedmaxpercent','opf']
    exclude = ('vgsize','vguuid','vgpesize','vgtotalpe','vgfreepe',)
    def has_add_permission(self, request):
        return False
admin.site.register(VG,VGAdmin)


def delete_iscsi_target(StatsAdmin,request,queryset):
    for obj in queryset:
        p = PollServer(obj.targethost)
        if p.DeleteTarget(obj.iqntar)==1:
            #p.GetTargetsState()
            obj.delete()



class TargetAdmin(StatsAdmin):
    readonly_fields = ('targethost','iqnini','iqntar','sizeinGB','owner','sessionup','rkb','wkb','rkbpm','wkbpm')
    list_display = ['iqntar','created_at','sizeinGB','aagroup','rkbpm','wkbpm','rkb','wkb','sessionup']
    actions = [delete_iscsi_target]
    search_fields = ['iqntar']
    stats = (Sum('sizeinGB'),)
    def has_add_permission(self, request):
        return False
#    def has_delete_permission(self, request, obj=None): # note the obj=None
#                return False

    def has_change_permission(self, request, obj=None):
        has_class_permission = super(TargetAdmin, self).has_change_permission(request, obj)
        if not has_class_permission:
            return False
        if obj is not None and not request.user.is_superuser and request.user.id != obj.owner.id:
            return False
        return True
    
    def aagroup(self,obj):
        try:
            name = AAGroup.objects.get(target=obj).name
            return name
        except:
            return "No AAGroup"
        
    def iscsi_storeip1(self, obj):
        return obj.targethost.storageip1

    def iscsi_storeip2(self, obj):
        return obj.targethost.storageip2

    def queryset(self, request):
        if request.user.is_superuser:
            return Target.objects.all()
        return Target.objects.filter(owner=request.user)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.owner = request.user
        obj.save()




class LVAdmin(StatsAdmin):
    readonly_fields = ('target','vg','lvname','lvsize','lvuuid','lvthinmapped','created_at')
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

    def has_add_permission(self, request):
        return False

#admin.site.register(Provisioner)
admin.site.register(Target, TargetAdmin)
admin.site.register(LV,LVAdmin)
#admin.site.register(AAGroup)
#admin.site.register(HostGroup)

class StorageHostForm(forms.ModelForm):
    class Meta:
        model = StorageHost
	
    def clean_dnsname(self):
#        featuredCount = Country.objects.filter(featured=True).count()
 
 #       if featuredCount >= 5 and self.cleaned_data['featured'] is True:
 #           raise forms.ValidationError("5 Countries can be featured at most!")
 #       return self.cleaned_data['featured']a
	saturnserver = self.cleaned_data['dnsname']
        try:
            p = PollServer(saturnserver)
            p.InstallScripts()
        except:
            raise forms.ValidationError("Error with Saturn Server "+saturnserver)
            logger.warn("Error with Saturn server specified on the form "+saturnserver)
	return self.cleaned_data['dnsname']
             
 
class StorageHostAdmin(admin.ModelAdmin):
    form = StorageHostForm
    list_display=['dnsname','ipaddress','storageip1','storageip2','created_at','updated_at']
admin.site.register(StorageHost, StorageHostAdmin)



#Code for bringing extended user attributes to Django admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from ssdfrontend.models import Profile

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'

class UserAdmin(UserAdmin):
    inlines = (ProfileInline,)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

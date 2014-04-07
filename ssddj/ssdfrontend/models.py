from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Provisioner(models.Model):
    #owner = models.ForeignKey(User)
    clienthost = models.CharField(max_length=100)
    sizeinGB = models.FloatField()
    serviceName = models.CharField(max_length=100)
    #target = models.ForeignKey('Target')
#    created_at = models.DateTimeField(auto_now_add=True)
#    updated_at = models.DateTimeField(auto_now=True)
    def __unicode__(self):              # __unicode__ on Python 2
        return self.clienthost


class LV(models.Model):
    target = models.ForeignKey('Target')
    vg = models.ForeignKey('VG')
    lvname = models.CharField(max_length=50,default='Not found')
    lvsize = models.FloatField()
    lvuuid = models.CharField(max_length=100,primary_key=True)
    lvthinmapped = models.FloatField(default=-1)
#    created_at = models.DateTimeField(auto_now_add=True,blank=True, null=True)
#    updated_at = models.DateTimeField(auto_now=True,blank=True, null=True)
    def __unicode__(self):              # __unicode__ on Python 2
        return self.lvname
#    def lvsize(self):
#        return self.lvsize
#    def lvname(self):
#        return self.lvname
#    deleted_at = models.DateTimeField()

class VG (models.Model):
    vghost = models.ForeignKey('StorageHost')
    vgsize = models.FloatField()
    vguuid = models.CharField(max_length=100,primary_key=True)
    vgpesize = models.FloatField()
    vgtotalpe = models.FloatField()
    vgfreepe = models.FloatField(default=-1)
    thinusedpercent = models.FloatField(default=-1)
    thintotalGB = models.FloatField(default=-1)
    maxthinavlGB = models.FloatField(default=-1)
    opf = models.FloatField(default=0.7)
    thinusedmaxpercent = models.FloatField(default=70)
    enabled = models.BooleanField(default=True)
    CurrentAllocGB = models.FloatField(default=-100.0)
    def __unicode__(self):              # __unicode__ on Python 2
        return self.vguuid

class StorageHost(models.Model):
    dnsname = models.CharField(max_length=100,primary_key=True)
    ipaddress = models.GenericIPAddressField(default='127.0.0.1')
    storageip1 = models.GenericIPAddressField(default='127.0.0.1')
    storageip2 = models.GenericIPAddressField(default='127.0.0.1')
    enabled = models.BooleanField(default=True)
  #  created_at = models.DateTimeField(auto_now_add=True,blank=True, null=True)
  #  updated_at = models.DateTimeField(auto_now=True,blank=True, null=True)
    def __unicode__(self):              # __unicode__ on Python 2
        return self.dnsname




class Target(models.Model):
    owner = models.ForeignKey(User)
    targethost= models.ForeignKey('StorageHost')
    iqnini = models.CharField(max_length=100)
    iqntar = models.CharField(max_length=100,primary_key=True)
    clienthost = models.CharField(max_length=100)
    sizeinGB = models.FloatField(max_length=100)
#    aagroup = models.ForeignKey(AAGroup, null=True, blank=True)
    sessionup = models.BooleanField(default=False)
    rkb = models.BigIntegerField(default=0)
    rkbpm = models.BigIntegerField(default=0)
    wkb = models.BigIntegerField(default=0)
    wkbpm = models.BigIntegerField(default=0)
   # created_at = models.DateTimeField(auto_now_add=True)
   # updated_at = models.DateTimeField(auto_now=True)
    def __unicode__(self):              # __unicode__ on Python 2
        return self.iqntar



class AAGroup(models.Model):
    name = models.CharField(max_length=100)
    hosts = models.ManyToManyField(StorageHost)
    target = models.ForeignKey(Target,null=True, blank=True)

    def __unicode__(self):
        return self.name 

from django.contrib.auth.models import User

#http://www.igorsobreira.com/2010/12/11/extending-user-model-in-django.html
class Profile(models.Model):
    user = models.OneToOneField(User,unique=True)
    max_target_sizeGB = models.FloatField(default=100.0)
    max_alloc_sizeGB = models.FloatField(default=400.0)


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

from django.db.models import signals
signals.post_save.connect(create_user_profile, sender=User)


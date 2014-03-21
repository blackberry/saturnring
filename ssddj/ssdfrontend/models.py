from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Provisioner(models.Model):
    #owner = models.ForeignKey(User)
    clienthost = models.CharField(max_length=100)
    sizeinGB = models.FloatField()
    serviceName=models.CharField(max_length=100)

#    created_at = models.DateTimeField(auto_now_add=True)
#    updated_at = models.DateTimeField(auto_now=True)
    def __unicode__(self):              # __unicode__ on Python 2
        return self.clienthost


class LV(models.Model):
    target = models.ForeignKey('Target')
    vg = models.ForeignKey('VG')
    lvname = models.CharField(max_length=50)
    lvsize = models.FloatField()
    lvuuid = models.CharField(max_length=100,primary_key=True)
    lvthinmapped = models.FloatField(default=-1)
#    created_at = models.DateTimeField(auto_now_add=True,blank=True, null=True)
#    updated_at = models.DateTimeField(auto_now=True,blank=True, null=True)
    def __unicode__(self):              # __unicode__ on Python 2
        return self.lvname

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
 #   created_at = models.DateTimeField(auto_now_add=True,blank=True, null=True)
 #   updated_at = models.DateTimeField(auto_now=True,blank=True, null=True)
    def __unicode__(self):              # __unicode__ on Python 2
        return self.vguuid

class StorageHost(models.Model):
    dnsname = models.CharField(max_length=100,primary_key=True)
    ipaddress = models.GenericIPAddressField(default='127.0.0.1')
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
    sizeinGB = models.CharField(max_length=100)
   # created_at = models.DateTimeField(auto_now_add=True)
   # updated_at = models.DateTimeField(auto_now=True)
    def __unicode__(self):              # __unicode__ on Python 2
        return self.iqntar






#Copyright 2014 Blackberry Limited
#
#Licensed under the Apache License, Version 2.0 (the "License");
#you may not use this file except in compliance with the License.
#You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#Unless required by applicable law or agreed to in writing, software
#distributed under the License is distributed on an "AS IS" BASIS,
#WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#See the License for the specific language governing permissions and
#limitations under the License.

from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Provisioner(models.Model):
    clientiqn = models.CharField(max_length=100)
    sizeinGB = models.FloatField()
    serviceName = models.CharField(max_length=100)
    def __unicode__(self):              # __unicode__ on Python 2
        return self.clientiqn


class LV(models.Model):
    target = models.ForeignKey('Target')
    vg = models.ForeignKey('VG')
    lvname = models.CharField(max_length=200,default='Not found')
    lvsize = models.FloatField()
    lvuuid = models.CharField(max_length=200,primary_key=True)
    lvthinmapped = models.FloatField(default=-1)
    created_at = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True,blank=True, null=True)
    def __unicode__(self):              # __unicode__ on Python 2
        return self.lvname

class Lock(models.Model):
    lockname=models.CharField(max_length=100,primary_key=True)
    locked = models.BooleanField(default=False)

    def __unicode__(self):
        return self.lockname

class VG (models.Model):
    vghost = models.ForeignKey('StorageHost')
    vgsize = models.FloatField()
    vguuid = models.CharField(max_length=200,primary_key=True)
    vgpesize = models.FloatField()
    vgtotalpe = models.FloatField()
    vgfreepe = models.FloatField(default=-1)
    thinusedpercent = models.FloatField(default=-1)
    thintotalGB = models.FloatField(default=-1)
    maxthinavlGB = models.FloatField(default=-1)
    opf = models.FloatField(default=0.99)
    thinusedmaxpercent = models.FloatField(default=99)
    enabled = models.BooleanField(default=True)
    CurrentAllocGB = models.FloatField(default=-100.0,null=True)
    created_at = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True,blank=True, null=True)
    is_locked = models.BooleanField(default=False)
    in_error = models.BooleanField(default=False)
    storemedia = models.CharField(max_length=200,default='unassigned',choices=[('unassigned','unassigned'),('pciessd','pciessd'),('diskssd','diskssd')])
    def __unicode__(self):              # __unicode__ on Python 2
        return self.vguuid


class StorageHost(models.Model):
    dnsname = models.CharField(max_length=200,primary_key=True)
    ipaddress = models.GenericIPAddressField(default='127.0.0.1')
    storageip1 = models.GenericIPAddressField(default='127.0.0.1')
    storageip2 = models.GenericIPAddressField(default='127.0.0.1')
    enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True,blank=True, null=True)
    def __unicode__(self):              # __unicode__ on Python 2
        return self.dnsname


class Target(models.Model):
    owner = models.ForeignKey(User)
    targethost= models.ForeignKey('StorageHost')
    iqnini = models.CharField(max_length=200)
    iqntar = models.CharField(max_length=200,primary_key=True)
    sizeinGB = models.FloatField(max_length=200)
    sessionup = models.BooleanField(default=False)
    rkb = models.BigIntegerField(default=0)
    rkbpm = models.BigIntegerField(default=0)
    wkb = models.BigIntegerField(default=0)
    wkbpm = models.BigIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True,blank=True, null=True)
    storageip1 = models.GenericIPAddressField(default='127.0.0.1')
    storageip2 = models.GenericIPAddressField(default='127.0.0.1')

    def __unicode__(self):              # __unicode__ on Python 2
        return self.iqntar


class TargetHistory(models.Model):
    owner = models.ForeignKey(User)
    iqntar=models.CharField(max_length=200)
    iqnini= models.CharField(max_length=200,blank=True,null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    deleted_at = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    sizeinGB=models.FloatField(max_length=200)
    rkb=models.BigIntegerField(default=0)
    wkb=models.BigIntegerField(default=0)


class AAGroup(models.Model):
    name = models.CharField(max_length=200)
    hosts = models.ManyToManyField(StorageHost)
    target = models.ForeignKey(Target,null=True, blank=True)

    def __unicode__(self):
        return self.name


class ClumpGroup(models.Model):
    name = models.CharField(max_length=200)
    hosts = models.ManyToManyField(StorageHost)
    target = models.ForeignKey(Target,null=True,blank=True)

    def __unicode__(self):
        return self.name


class IPRange(models.Model):
    owner = models.ForeignKey(User)
    iprange = models.CharField(max_length=20)
    hosts = models.ManyToManyField(StorageHost)

    def __unicode__(self):
        return self.iprange


class Interface(models.Model):
    storagehost = models.ForeignKey(StorageHost)
    ip = models.CharField(max_length=15)
    iprange = models.ManyToManyField(IPRange)
    owner=models.ForeignKey(User,null=True)

    def __unicode__(self):
        return self.ip

from django.contrib.auth.models import User

#http://www.igorsobreira.com/2010/12/11/extending-user-model-in-django.html
class Profile(models.Model):
    user = models.OneToOneField(User,unique=True)
    max_target_sizeGB = models.FloatField(default=5)
    max_alloc_sizeGB = models.FloatField(default=10)


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

from django.db.models import signals
signals.post_save.connect(create_user_profile, sender=User,dispatch_uid='autocreate_nuser')


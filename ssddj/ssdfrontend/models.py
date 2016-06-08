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
import string
from uuid import uuid4
# Create your models here.
from django.core.exceptions import ValidationError

def validate_nospecialcharacters(value):
    invalidcharacters = set(string.punctuation.replace("_", "").replace("-",""))
    if len(invalidcharacters.intersection(value)):
        raise ValidationError(u'%s contains a special character, retry after removing it' % value)

def validate_sizeinGB(sizeinGB):
    if sizeinGB < 1.0:
        raise ValidationError("Require sizeinGB >= 1.0")

def validate_clientiqn(clientiqn):
    if not (clientiqn.startswith('iqn.')):# and clientiqn.endswith('.ini')):
        raise ValidationError("clientiqn should be of the form iqn.*.ini")

def GenerateRandomPin():
    d = uuid4()
    str = d.hex
    return str[0:8]

class Provisioner(models.Model):
    clientiqn = models.CharField(max_length=100,validators=[validate_clientiqn])
    sizeinGB = models.FloatField(validators=[validate_sizeinGB])
    serviceName = models.CharField(max_length=100,validators=[validate_nospecialcharacters])
    def __unicode__(self):              # __unicode__ on Python 2
        return self.clientiqn


class LV(models.Model):
    target = models.ForeignKey('Target')
    vg = models.ForeignKey('VG')
    lvname = models.CharField(max_length=200,default='Not found')
    lvsize = models.FloatField()
    lvuuid = models.CharField(max_length=200,primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True,blank=True, null=True)
    isencrypted = models.BooleanField(default=False)

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
    totalGB = models.FloatField(default=-1)
    maxavlGB = models.FloatField(default=-1)
    enabled = models.BooleanField(default=True)
    CurrentAllocGB = models.FloatField(default=-100.0,null=True)
    created_at = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True,blank=True, null=True)
    is_locked = models.BooleanField(default=False)
    in_error = models.BooleanField(default=False)
    storemedia = models.CharField(max_length=200,default='unassigned',choices=[('unassigned','unassigned'),('PCIEcard1','PCIEcard1',),('PCIEcard2','PCIEcard2',),('PCIEcard3','PCIEcard3',)])
    is_thin = models.BooleanField(default=True)
    def __unicode__(self):              # __unicode__ on Python 2
        return 'SERVER:'+str(self.vghost)+':VG:'+str(self.vguuid)


class StorageHost(models.Model):
    dnsname = models.CharField(max_length=200,primary_key=True)
    ipaddress = models.GenericIPAddressField(default='127.0.0.1')
    storageip1 = models.GenericIPAddressField(default='127.0.0.1')
    storageip2 = models.GenericIPAddressField(default='127.0.0.1')
    enabled = models.BooleanField(default=True)
    snaplock = models.BooleanField(default=False)
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
    isencrypted = models.BooleanField(default=False)
    pin = models.CharField(max_length=32,default=GenerateRandomPin)

    def __unicode__(self):              # __unicode__ on Python 2
        return self.iqntar

class TargetNameMap(models.Model):
    owner = models.ForeignKey(User)
    oldtarname = models.CharField(max_length=200)
    newtarname = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True,blank=True, null=True)


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

class SnapJob(models.Model):
    numsnaps = models.IntegerField(default=1)
    iqntar = models.ForeignKey(Target)
    cronstring = models.CharField(max_length=100)
    lastrun = models.DateTimeField(blank=True)
    nextrun = models.DateTimeField(blank=True)
    created_at = models.DateTimeField(blank=True, null=True)
    deleted_at = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    enqueued = models.BooleanField(blank=False,default=False)
    run_now = models.BooleanField(blank=False,default=False)

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
    user = models.OneToOneField(User,unique=True,primary_key=True,on_delete=models.CASCADE)
    max_target_sizeGB = models.FloatField(default=0)
    max_alloc_sizeGB = models.FloatField(default=0)


def create_user_profile(sender, **kwargs):
    if kwargs["created"]:
        Profile.objects.get_or_create(user=kwargs["instance"])

from django.db.models import signals
signals.post_save.connect(create_user_profile, sender=User,dispatch_uid='autocreate_nuser')


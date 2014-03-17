from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Provisioner(models.Model):
    clienthost = models.CharField(max_length=100)
    sizeinGB = models.FloatField()
    serviceName=models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class LV(models.Model):
    target = models.ForeignKey('Target')
    vg = models.ForeignKey('VG')
    lvname = models.CharField(max_length=50)
    lvsize = models.FloatField()
    lvuuid = models.CharField(max_length=100,primary_key=True)
    lvthinmapped = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
#    deleted_at = models.DateTimeField()

class VG (models.Model):
    vghost = models.ForeignKey('StorageHost')
    vgsize = models.FloatField()
    vguuid = models.CharField(max_length=100,primary_key=True)
    vgpesize = models.FloatField()
    vgtotalpe = models.FloatField()
    vgfreepe = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class StorageHost(models.Model):
    dnsname = models.CharField(max_length=100,primary_key=True)
    ipaddress = models.GenericIPAddressField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Target(models.Model):
    owner = models.ForeignKey(User)
    targethost= models.ForeignKey('StorageHost')
    iqnini = models.CharField(max_length=100)
    iqntar = models.CharField(max_length=100,primary_key=True)
    clienthost = models.CharField(max_length=100)
    sizeinGB = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)





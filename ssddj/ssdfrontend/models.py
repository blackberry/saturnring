from django.db import models

class Lun(models.Model):
    iqnname = models.CharField(max_length=100)
# Create your models here.

class LV(models.Model):
    lvhost = models.ForeignKey('StorageHost')
    vg = models.ForeignKey('VG')
    lvname = models.CharField(max_length=50)
    lvsize = models.FloatField()
    lvuuid = models.CharField(max_length=100,unique=True)
    lvthin = models.BooleanField()
    lvthinused = models.FloatField()

class VG (models.Model):
    vghost = models.ForeignKey('StorageHost')
    vgsize = models.FloatField()
    vguuid = models.CharField(max_length=100,unique=True)
    vgpesize = models.IntegerField()
    vgtotalpe = models.IntegerField()
    vgfreepe = models.IntegerField()

class StorageHost(models.Model):
    dnsname = models.CharField(max_length=100,unique=True)
    ipaddress = models.GenericIPAddressField()



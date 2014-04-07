from rest_framework import serializers

from  ssdfrontend.models import Target 
from  ssdfrontend.models import Provisioner
from ssdfrontend.models import VG
class ProvisionerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provisioner
        fields = ('clientiqn','sizeinGB','serviceName')
class TargetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Target
        fields = ('iqnini','iqntar')
class VGSerializer(serializers.ModelSerializer):
    class Meta:
            model = VG




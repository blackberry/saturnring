from rest_framework import serializers

from  ssdfrontend.models import Target 
from  ssdfrontend.models import Provisioner
class ProvisionerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Provisioner
        fields = ('clienthost','sizeinGB','serviceName')
class TargetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Target
        fields = ('iqnini','iqntar')




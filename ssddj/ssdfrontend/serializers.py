from rest_framework import serializers

from  ssdfrontend.models import Lun

class LunSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lun
        fields = ('iqnname')


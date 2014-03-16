from rest_framework import serializers

from  ssdfrontend.models import Target 

class TargetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Target
        fields = ('iqnname',)


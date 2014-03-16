from django.shortcuts import render
from api.serializers import TargetSerializer
from ssdfrontend.models import Target 
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from ssdfrontend.models import Target
from api.serializers import TargetSerializer

@api_view(['GET','POST'])
def targetlist(request):
    if (request.method == 'GET'):
        targets = Target.objects.all()
        serializer = TargetSerializer(targets)
        return Response(serializer.data)
    else:
        if request.method =='POST':
            serializer = TargetSerializer(data=request.DATA)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data,status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def lvlist(request):
    if(request.method=='GET'):
        lvs = lvscan()
        serializer = LVSerializer(lvs)
        return Response(serializer.data)


# Create your views here.

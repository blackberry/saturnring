from django.shortcuts import render
from ssdfrontend.serializers import LunSerializer
from ssdfrontend.models import Lun

@api_view(['GET','POST'])
def lunlist(request):
    if (request.method == 'GET'):
        luns = Luns.objects.all()
        serializer = LunSerializer(luns)
        return Response(serializer.data)
    else
        (if request.method =='POST'):
            serializer = LunSerializer(Lun,request.DATA)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            else
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# Create your views here.

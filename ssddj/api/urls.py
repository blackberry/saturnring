from django.conf.urls import patterns,url

urlpatterns = patterns(
    'api.views',
    url(r'^maketarget/$','MakeTarget',name='MakeTarget'),
)



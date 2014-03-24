from ssdfrontend import views
from django.conf.urls import patterns, include, url
from ssdfrontend.views import TargetList

urlpatterns = patterns('',
            url(r'^targets/$', TargetList.as_view()),
            )


from django.conf.urls import patterns, include, url
from  snapbackup import views

urlpatterns = patterns('',
    url(r'^config/$', views.SnapConfigView.as_view(),name='snapconfignull' ),
    url(r'^config/(?P<targets>.+)/$', views.SnapConfigView.as_view(),name='snapconfig' ),
    )


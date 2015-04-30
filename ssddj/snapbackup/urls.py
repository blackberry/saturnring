
from django.conf.urls import patterns, include, url
from  snapbackup import views

urlpatterns = patterns('',
    url(r'^create/', views.SnapJobCreateView.as_view(),name='snapcreate'),
    )



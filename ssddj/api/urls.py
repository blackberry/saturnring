from django.conf.urls import patterns, url
from rest_framework.urlpatterns import format_suffix_patterns
import views

urlpatterns = patterns('',
            url(r'^provisioner/$', views.Provision.as_view()),
            url(r'^targets/(?P<pk>[0-9]+)/$', views.TargetDetail.as_view()),
            url(r'^vgscan/$', views.VGScanner.as_view()),
            url(r'^stateupdate/$',views.UpdateStateData.as_view()),
                )

urlpatterns = format_suffix_patterns(urlpatterns)

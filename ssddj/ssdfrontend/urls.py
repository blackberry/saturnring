from ssdfrontend import views
from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^lun-form/$', views.lun_form),

                    )

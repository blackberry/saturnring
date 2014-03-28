from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^api/', include('api.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^portal/',include('ssdfrontend.urls')),
)
urlpatterns += patterns('',
    (r'^django-rq/', include('django_rq.urls')),
)

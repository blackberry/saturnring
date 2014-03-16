from django.conf.urls import patterns,url

urlpatterns = patterns(
    'api.views',
    url(r'^targetlist/$','targetlist',name='targetlist'),
)



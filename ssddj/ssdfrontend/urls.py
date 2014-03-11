from django.conf.urls import patterns,url
url.patterns = patterns(
        'ssdfrontend.views',
        url('r/lunlist/$','lunlist',name='lunlist'),
        )



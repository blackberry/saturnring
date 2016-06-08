#Copyright 2014 Blackberry Limited
#
#Licensed under the Apache License, Version 2.0 (the "License");
#you may not use this file except in compliance with the License.
#You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#Unless required by applicable law or agreed to in writing, software
#distributed under the License is distributed on an "AS IS" BASIS,
#WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#See the License for the specific language governing permissions and
#limitations under the License.

from django.conf.urls import patterns, url
from rest_framework.urlpatterns import format_suffix_patterns
import views

urlpatterns = patterns('',
            url(r'^provisioner/$', views.Provision.as_view()),
            url(r'^delete/$', views.Delete.as_view()),
            url(r'^vgscan/$', views.VGScanner.as_view()),
            url(r'^stateupdate/$',views.UpdateStateData.as_view()),
            url(r'^stats/$',views.ReturnStats.as_view()),
            url(r'^userstats/$',views.ReturnUserStats.as_view()),
            url(r'^targetportal/$',views.ReturnTargetPortal.as_view()),
            # Commented out because this is not really implemented fully - 
            #does not change DB entry, it only changes SCST file: inconsistency introducted.
            #url(r'^changeinitiator/$',views.ChangeInitiator.as_view()),
            url(r'^changetarget/$',views.ChangeTarget.as_view()),
                )

urlpatterns = format_suffix_patterns(urlpatterns)

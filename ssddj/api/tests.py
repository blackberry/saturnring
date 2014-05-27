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

from django.test import TestCase
from ssdfrontend.models import VG
from subprocess import check_output
# Create your tests here.
class APITestCase (TestCase):
    def setUp(self):
        print "Here is where we can set some state"

    def test_UpdateStateData(self):
        outStr=check_output(["curl","-X","GET","http://127.0.0.1/saturnring/api/stateupdate/"])
        print outStr
    
    def test_Provisioner(self):
        try:
            outStr=check_output(["curl","-s","-X","GET","http://127.0.0.1/saturnring/api/provisioner/",
                "-d",'clientiqn=testclient&sizeinGB=1.0&serviceName=testservice&aagroup=testgroup',
                "-u","testuser:password"])
            print outStr
        except:
            print "This did not work"

   

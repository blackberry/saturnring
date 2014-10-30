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
from subprocess import check_output
import traceback
from pprint import pprint

from ssdfrontend.models import VG
from ssdfrontend.models import StorageHost
from ssdfrontend.models import LV
from ssdfrontend.models import Target
from globalstatemanager.gsm import PollServer
# Create your tests here.
class GSMTestCase (TestCase):
    """ Test cases for GlobalStatemanager
            Test GetLVs
            Test GetVGs
    """

    def setUp(self):
        """
        Setup the test saturn host (where the storage is provisioned)
        Assuming a VG exists on that host, run VGscan 
        This means that the SSH key should be on that host already
        """
        print "Here is where we can set some state"
        self.saturnringip = "127.0.0.1"
        self.saturnringport = "8000"
        self.testip = "192.168.61.21"
        testhost = StorageHost(dnsname = self.testip,
                ipaddress=self.testip,
                storageip1=self.testip
                )
        testhost.save()
        outStr = check_output(["curl","-X","GET","http://"+self.saturnringip+":"+self.saturnringport+"/api/vgscan/","-d","saturnserver="+self.testip])
        print outStr
        vguuid = outStr.split('"')[3]
        vg = VG(vghost=testhost,
                vguuid = vguuid,
                vgpesize = 1.0,
                vgtotalpe = 10.0,
                vgsize = 1.0)
        vg.save()
        outStr = check_output(["curl","-X","GET","http://"+self.saturnringip+":"+self.saturnringport+"/api/vgscan/","-d","saturnserver="+self.testip])

    def test_GetLVs(self):
        """
        """
        shost = StorageHost.objects.all()[0]
        vguuid = VG.objects.all()[0].vguuid
        ps = PollServer(shost.dnsname)
        lvs = ps.GetLVs(vguuid)
        print lvs
        self.assertNotEqual(len(lvs),0)



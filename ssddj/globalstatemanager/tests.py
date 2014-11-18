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

#globalstatemanager/tests.py

from django.test import TestCase
from django.contrib.auth.models import User
from subprocess import check_output
from traceback import format_exc
from pprint import pprint
from utils.configreader import ConfigReader

from ssdfrontend.models import VG
from ssdfrontend.models import StorageHost
from ssdfrontend.models import LV
from ssdfrontend.models import Target
from ssdfrontend.models import Interface
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
        #Dummy super user for interfaces test
        config = ConfigReader('saturn.ini')
        self.saturnringip = config.get('tests','saturnringip')
        self.saturnringport = config.get('tests','saturnringport')
        self.iscsiserver = config.get('tests','saturniscsiserver')
        my_admin = User.objects.create_superuser('myuser', 'myemail@test.com', 'password')
        testhost = StorageHost(dnsname = self.iscsiserver,
                ipaddress=self.iscsiserver,
                storageip1=self.iscsiserver
                )
        testhost.save()
        outStr = check_output(["curl","-X","GET","http://"+self.saturnringip+":"+self.saturnringport+"/api/vgscan/","-d","saturnserver="+self.iscsiserver])
        vguuid = outStr.split('"')[3]
        vg = VG(vghost=testhost,
                vguuid = vguuid,
                vgpesize = 1.0,
                vgtotalpe = 10.0,
                vgsize = 1.0)
        vg.save()
        outStr = check_output(["curl","-X","GET","http://"+self.saturnringip+":"+self.saturnringport+"/api/vgscan/","-d","saturnserver="+self.iscsiserver])

    def test_GetLVs(self):
        """
        Test if LVs are being read off the test server
        """
        shost = StorageHost.objects.all()[0]
        vguuid = VG.objects.all()[0].vguuid
        ps = PollServer(shost.dnsname)
        lvs = ps.GetLVs(vguuid)
        pprint(lvs)
        self.assertNotEqual(len(lvs),0)


    def test_Exec(self):
        """
        Test if SSH/Exec works
        """
        shost = StorageHost.objects.all()[0]
        ps = PollServer(shost.dnsname)
        rtnStr = ps.Exec("uptime")
        self.assertIn("load average",str(rtnStr))

    def test_GetInterfaces(self):
        """
        Test if the interface scanning works
        """
        shost = StorageHost.objects.all()[0]
        ps = PollServer(shost.dnsname)
        oldEntries = Interface.objects.all()
        oldEntries.delete()
        ps.GetInterfaces()
        interfaces = Interface.objects.all()
        for eachInterface in interfaces:
            print eachInterface.ip

        self.assertNotEqual(len(interfaces), 0)

    def test_InstallScripts(self):
        """
        Test the installation of scripts
        Also a good test for SSH keys etc.
        """









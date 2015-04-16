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
from utils.configreader import ConfigReader

# Create your tests here.
class APITestCase (TestCase):
    """ Test cases for API
            Test stateupdate
            Test provision
            Test delete
            Test stats
    """

    def setUp(self):
        print "Here is where we can set some state"
        config = ConfigReader('saturn.ini')
        self.saturnringip = config.get('tests','saturnringip')
        self.saturnringport = config.get('tests','saturnringport')
        self.iscsiserver = config.get('tests','saturniscsiserver')
        
    def test_UpdateStateData(self):
        print "TESTING UpdateStateData"
        outStr = check_output(["curl","-X","GET","http://"+self.saturnringip+":"+self.saturnringport+"/api/stateupdate/"])
        self.assertIn('Ok, enqueued state update request', outStr)
        print outStr
    
    def test_Provisioner(self):
        """
            Test the provisioning call

            Note: needs an account to be setup in the portal
            testuser/password
        """
        print "TESTING Provisioner"
        outStr = check_output(["curl","-X","GET",
            "http://"+self.saturnringip+":"+self.saturnringport+"/api/provisioner/",
            "-d",'clientiqn=testclient&sizeinGB=1.0&serviceName=testserviceprovisionrandom&aagroup=testgroup',
            "-u","testuser:password",])
        self.assertIn('"error": 0',outStr)
        print outStr

    def test_DeletionTarget(self):
        """
            Test the deletion call for 1 target
            Note: needs an account to be setup in the portal
            testuser/password

        """
        print "TESTING DeletionTarget"
        print "Creating target if it doesnt exist"
        outStr = check_output(["curl","-X","GET",
            "http://"+self.saturnringip+":"+self.saturnringport+"/api/provisioner/",
            "-d",'clientiqn=testclient&sizeinGB=1.0&serviceName=testserviceprovisionrandom&aagroup=testgroup',
            "-u","testuser:password",])
        print outStr
        print "Deleting target"
        outStr = check_output(["curl","-X","GET",
            "http://"+self.saturnringip+":"+self.saturnringport+"/api/delete/",
            "-d","iqntar=iqn.2014.01."+self.iscsiserver+":testserviceprovisionrandom:aa59eb0a",
            "-u","testuser:password"])
        print outStr
        self.assertIn('"error": 0',outStr)
        print outStr

    def test_ProvisionerThin(self):
        """
            Test the provisioning call

            Note: needs an account to be setup in the portal
            testuser/password
        """
        print "TESTING Provisioner"
        outStr = check_output(["curl","-X","GET",
            "http://"+self.saturnringip+":"+self.saturnringport+"/api/provisioner/",
            "-d",'clientiqn=testclient&sizeinGB=1.0&serviceName=testserviceprovisionthin&aagroup=testgroup&provisiontype=1',
            "-u","testuser:password",])
        self.assertIn('"error": 0',outStr)
        print outStr

    def test_DeletionTargetThin(self):
        """
            Test the deletion call for 1 target
            Note: needs an account to be setup in the portal
            testuser/password

        """
        print "TESTING DeletionTarget"
        print "Creating target if it doesnt exist"
        outStr = check_output(["curl","-X","GET",
            "http://"+self.saturnringip+":"+self.saturnringport+"/api/provisioner/",
            "-d",'clientiqn=testclient&sizeinGB=1.0&serviceName=testserviceprovisionthin&aagroup=testgroup&provisiontype=1',
            "-u","testuser:password",])
        print outStr
        print "Deleting target"
        outStr = check_output(["curl","-X","GET",
            "http://"+self.saturnringip+":"+self.saturnringport+"/api/delete/",
            "-d","iqntar=iqn.2014.01."+self.iscsiserver+":testserviceprovisionthin:aa59eb0a",
            "-u","testuser:password"])
        self.assertIn('"error": 0',outStr)
        print outStr

    def test_ProvisionerThick(self):
        """
            Test the provisioning call

            Note: needs an account to be setup in the portal
            testuser/password
        """
        print "TESTING Provisioner"
        outStr = check_output(["curl","-X","GET",
            "http://"+self.saturnringip+":"+self.saturnringport+"/api/provisioner/",
            "-d",'clientiqn=testclient&sizeinGB=1.0&serviceName=testserviceprovisionthick&aagroup=testgroup&provisiontype=0',
            "-u","testuser:password",])
        self.assertIn('"error": 0',outStr)
        print outStr

    def test_DeletionTargetThick(self):
        """
            Test the deletion call for 1 target
            Note: needs an account to be setup in the portal
            testuser/password

        """
        print "TESTING DeletionTarget"
        print "Creating target if it doesnt exist"
        outStr = check_output(["curl","-X","GET",
            "http://"+self.saturnringip+":"+self.saturnringport+"/api/provisioner/",
            "-d",'clientiqn=testclient&sizeinGB=1.0&serviceName=testserviceprovisionthick&aagroup=testgroup&provisiontype=0',
            "-u","testuser:password",])
        print outStr
        print "Deleting target"
        outStr = check_output(["curl","-X","GET",
            "http://"+self.saturnringip+":"+self.saturnringport+"/api/delete/",
            "-d","iqntar=iqn.2014.01."+self.iscsiserver+":testserviceprovision:aa59eb0a",
            "-u","testuser:password"])
        self.assertIn('"error": 0',outStr)
        print outStr

    def test_VGScan(self):
        print "TESTING VGScan"
        outStr = check_output(["curl","-X","GET",
        "http://"+self.saturnringip+":"+self.saturnringport+"/api/vgscan/",
        "-d","saturnserver="+self.iscsiserver])
        print outStr
        self.assertIn('vguuid',outStr)

    def tearDown(self):
        print "Attempting to clean up"
        print "Deleting"
        outStr = check_output(["curl","-X","GET",
            "http://"+self.saturnringip+":"+self.saturnringport+"/api/delete/",
            "-d","iqntar=iqn.2014.01.self.iscsiserver:testserviceprovision:aa59eb0a",
            "-u","testuser:password"])
        outStr = check_output(["curl","-X","GET",
            "http://"+self.saturnringip+":"+self.saturnringport+"/api/delete/",
            "-d","iqntar=iqn.2014.01.self.iscsiserver:testserviceprovisionthin:aa59eb0a",
            "-u","testuser:password"])
        outStr = check_output(["curl","-X","GET",
            "http://"+self.saturnringip+":"+self.saturnringport+"/api/delete/",
            "-d","iqntar=iqn.2014.01.self.iscsiserver:testserviceprovisionthick:aa59eb0a",
            "-u","testuser:password"])



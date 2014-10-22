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
        
    def test_UpdateStateData(self):
        print "TESTING UpdateStateData"
        outStr = check_output(["curl","-X","GET","http://127.0.0.1:8000/api/stateupdate/"])
        self.assertIn("Ok", outStr)
        print outStr
    
    def test_Provisioner(self):
        """
            Test the provisioning call

            Note: needs a account to be setup in the portal
            testuser/password
        """
        print "TESTING Provisioner"
        outStr = check_output(["curl","-X","GET",
            "http://127.0.0.1:8000/api/provisioner/",
            "-d",'clientiqn=testclient&sizeinGB=1.0&serviceName=testserviceprovision&aagroup=testgroup',
            "-u","testuser:password",])
        self.assertIn('"error": 0',outStr)
        print outStr

    def test_DeletionTarget(self):
        """
            Test the deletion call for 1 target

            Note: needs the test_Provisioner test to be run so that 
            the test has already been run
        """
        #First create a iSCSI target
        print "TESTING DeletionTarget"
        outStr = check_output(["curl","-X","GET",
            "http://127.0.0.1:8000/api/provisioner/",
            "-d",'clientiqn=testclient&sizeinGB=1.0&serviceName=testservicedelete1&aagroup=testgroup',
            "-u","testuser:password",])
        outStr = check_output(["curl","-X","GET",
            "http://127.0.0.1:8000/api/delete/",
            "-d","iqntar=iqn.2014.01.192.168.61.21:testservicedelete1:aa59eb0a",
            "-u","testuser:password"])
        self.assertIn('"error": 0',outStr)
        print outStr

    def test_DeletionClientIQN(self):
        """
            Test the deletion call for all targets created off a clientiqn for a specific user
        """

    def test_DeletionUserTargetStorageHost(self):

        """
            This is the deletion call for all targets belonging to a user  on a specified StorageHost
        """
    def test_VGScan(self):
        print "TESTING VGScan"
        outStr = check_output(["curl","-X","GET",
        "http://127.0.0.1:8000/api/vgscan/",
        "-d","saturnserver=192.168.61.21"])
        print outStr
        self.assertIn('vguuid',outStr)


    def tearDown(self):
        print "Attempting to clean up"
        print "Deleting"
        outStr = check_output(["curl","-X","GET",
            "http://127.0.0.1:8000/api/delete/",
            "-d","iqntar=iqn.2014.01.192.168.61.21:testserviceprovision:aa59eb0a",
            "-u","testuser:password"])



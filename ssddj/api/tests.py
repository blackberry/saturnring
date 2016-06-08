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
from xlrd import open_workbook, XLRDError
from uuid import uuid4
import json
# Create your tests here.
class APITestCase (TestCase):
    """ Test cases for API
            Test stateupdate
            Test provision
            Test delete
            Test stats
            Test changetarget
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
        self.assertIn('|||', outStr)
        print outStr
    
    def test_ProvisionerPlain(self):
        """
            Test the provisioning call

            Note: needs a account to be setup in the portal
            testuser/password
        """
        print "TESTING Provisioner"
        outStr = check_output(["curl","-X","GET",
            "http://"+self.saturnringip+":"+self.saturnringport+"/api/provisioner/",
            "-d",'clientiqn=iqn.testclient.ini&sizeinGB=1.0&serviceName=test-serviceprovision&aagroup=testgroup',
            "-u","testuser:password",])
        self.assertIn('"error": 0',outStr)
        print outStr

    def test_Provisioner_pcie1(self):
        """
            Test the provisioning call

            Note: needs a account to be setup in the portal
            testuser/password
        """
        print "TESTING Provisioner"
        outStr = check_output(["curl","-X","GET",
            "http://"+self.saturnringip+":"+self.saturnringport+"/api/provisioner/",
            "-d",'clientiqn=iqn.testclient.ini&sizeinGB=1.0&serviceName=testi-serviceprovisionpciessd&aagroup=testgroup&storemedia=PCIEcard1',
            "-u","testuser:password",])
        self.assertIn('"error": 0',outStr)
        print outStr

    def test_Provisioner_pcie2(self):
        """
            Test the provisioning call

            Note: needs a account to be setup in the portal
            testuser/password
        """
        print "TESTING Provisioner"
        outStr = check_output(["curl","-X","GET",
            "http://"+self.saturnringip+":"+self.saturnringport+"/api/provisioner/",
            "-d",'clientiqn=iqn.testclient.ini&sizeinGB=1.0&serviceName=test-serviceprovisiondiskssd3&aagroup=testgroup&storemedia=PCIEcard2',
            "-u","testuser:password",])
        self.assertIn('"error": 0',outStr)
        print outStr

    def test_Provisioner_diskssd_sameservicename(self):
        """
            Test the provisioning call, should fail to provision
            because it tries to create 2 identical targetnames on different media

            Note: needs a account to be setup in the portal
            testuser/password
        """
        print "TESTING Provisioner"
        outStr = check_output(["curl","-X","GET",
            "http://"+self.saturnringip+":"+self.saturnringport+"/api/provisioner/",
            "-d",'clientiqn=iqn.testclient.ini&sizeinGB=1.0&serviceName=test-serviceprovisiondsamebackend&aagroup=testgroup&storemedia=PCIEcard1',
            "-u","testuser:password",])
        outStr = check_output(["curl","-X","GET",
            "http://"+self.saturnringip+":"+self.saturnringport+"/api/provisioner/",
            "-d",'clientiqn=iqn.testclient.ini&sizeinGB=1.0&serviceName=test-serviceprovisiondsamebackend&aagroup=testgroup&storemedia=PCIEcard2',
            "-u","testuser:password",])
        self.assertIn('DIFFERENT storemedia',outStr)
        print outStr


    def test_Provisioner_UnEncrypted(self):
        """
            Test the provisioning call for encrypted targets

            Note: needs a account to be setup in the portal
            testuser/password
        """
        print "TESTING Provisioner for encrypted ta rgets"
        outStr = check_output(["curl","-X","GET",
            "http://"+self.saturnringip+":"+self.saturnringport+"/api/provisioner/",
            "-d",'clientiqn=iqn.testclient.ini&sizeinGB=1.0&serviceName=test-serviceprovisionnoenc&aagroup=testgroup&isencrypted=0',
            "-u","testuser:password",])
        print outStr


    def test_DeletionTargetPlain(self):
        """
            Test the deletion call for 1 target

            Note: needs the test_Provisioner test to be run so that 
            the target has already been created
        """
        print "TESTING DeletionTarget"
        outStr = check_output(["curl","-X","GET",
            "http://"+self.saturnringip+":"+self.saturnringport+"/api/delete/",
            "-d","iqntar=iqn.2014.01."+self.iscsiserver+":test-serviceprovision:aa59eb0a",
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
        "http://"+self.saturnringip+":"+self.saturnringport+"/api/vgscan/",
        "-d","saturnserver="+self.iscsiserver])
        print outStr
        self.assertIn('vguuid',outStr)

    def test_Stats(self):
        print "TESTING API stats excel return"
        outStr = check_output(["curl","-X","GET",
        "http://"+self.saturnringip+":"+self.saturnringport+"/api/stats/"
        ])
        with open('test.xls','wb') as f:
            f.write(outStr)
        xls = 'Returned XLS file not ok'
	try:
            book = open_workbook('test.xls')
            xls = 'ok'
        except XLRDError as e:
            print e
        self.assertEqual('ok',xls)

    def test_ChangeTarget(self):
        print "TESTING ChangeTarget"
        print "Setting up test target:"

        outStr = check_output(["curl","-X","GET", 
            "http://"+self.saturnringip+":"+self.saturnringport+"/api/provisioner/",
            "-d","clientiqn=iqn.originalclient.ini",
            "-d","sizeinGB=1.0",
            "-d","serviceName=originalservice"+str(uuid4())[:6],
            "-d","aagroup=testgroup",
            "-u","testuser:password"])
        self.assertIn('"error": 0',outStr)
        print "Changing test target IQN:"
        j = json.loads(outStr)
        iqntar = j["iqntar"]
        pin = j["pin"]
        outStr = check_output(["curl","-X","GET", 
            "http://"+self.saturnringip+":"+self.saturnringport+"/api/changetarget/",
            "-d","iqntar="+iqntar,
            "-d","pin="+pin,
            "-d","newserviceName=newservice"+str(uuid4())[:6],
            "-d","newini=iqn.newclient.ini",
            "-u","testuser:password"])
        self.assertIn('"error": 0',outStr)
        self.assertIn('newservice',outStr)
        
        print "Deleting test target: "
        newtar = json.loads(outStr)["iqntar"]
        outStr = check_output(["curl","-X","GET", 
            "http://"+self.saturnringip+":"+self.saturnringport+"/api/delete/",
            "-d","iqntar="+newtar,
            "-u","testuser:password"])
        print outStr
        self.assertIn('"error": 0',outStr)


    def tearDown(self):
        print "Attempting to clean up -  this will delete all iSCSI targets that belong to user testuser on the test iscsiserver"
        #outStr = check_output(["curl","-X","GET",
        #"http://"+self.saturnringip+":"+self.saturnringport+"/api/delete/",
        #"-d","targethost="+self.iscsiserver,
        #"-u","testuser:password"])





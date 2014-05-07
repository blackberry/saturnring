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

   

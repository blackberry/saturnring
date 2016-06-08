#!/bin/bash
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

#Test datastore driver (creation,deletion of images, migrations from legacy Saturn)
#To run:
#These test is run on the OpenNebula frontend, as oneadmin user
#fab test_image_create
#fab test_image_migrate
#Certain defaults are assumed (see the function parameters - replace via fab if needed)

from fabric.api import local
from fabric.contrib.console import confirm
from uuid import uuid4
from pprint import pprint
from time import sleep
import requests
import json
import sys

#Test creating a Saturn LUN-based OpenNebula image, and then deleting it
def test_image_create(datastore = "100",test_image_tpl_string=None,
        testimagename="testimage",deleteoption=True):
    if test_image_tpl_string is None:
        print "Testing Image Create..."
        test_image_tpl_string = """
        NAME = {testimagename}
        TYPE = DATABLOCK
        SIZE = 1000
        AAGROUP = testgroup
        DESCRIPTION = ThisIsATestImage
        PERSISTENT = Yes
        """.format(testimagename=testimagename)
    fH = open('test_image.tpl','w')
    fH.write(test_image_tpl_string)
    fH.close()
    command = ";".join(["oneimage create test_image.tpl -d "+datastore,"exit 0"])
    print command
    output = local(command)
    print output
    sleep(3)
    local("oneimage list")
    if deleteoption:
        if confirm("Delete test image ? "):
            command = ";".join(["oneimage delete "+testimagename,"exit 0"])
            local(command)
            sleep(3)
            local("oneimage list")
    

#Test migrating a legacy Saturn LUN to an OpenNebula image, and then delete it
def test_image_migrate(datastore = "100",
        saturnurl="http://192.168.50.50/api/provisioner/",
        user="oneuser",
        password="onepassword"):

    print "Testing Legacy image migration..."
    saturnauth = (user,password)
    saturndata = {'serviceName':'testservice','clientiqn':'iqn.testclient.ini','sizeinGB':1.0}
    r = requests.get(saturnurl,auth=saturnauth,data=saturndata)
    if r.status_code < 400:
        returneddic = json.loads(r.text)
        print "Created legacy test LUN:"
        pprint(returneddic)
        testimagename = "testimagemigrate"+uuid4().get_hex().upper()[0:6]
        test_image_tpl_string = """
        NAME = {testimagename}
        TYPE = DATABLOCK
        SIZE = 1000
        AAGROUP = testgroup
        DESCRIPTION = ThisIsATestImage
        PERSISTENT = Yes
        MIGRATEFROM = {iqntar}
        MIGRATEPIN = {pin}
        """.format(testimagename=testimagename,iqntar = returneddic['iqntar'],pin = returneddic['pin'])
        print "Creating OpenNebula Image from legacy LUN"
        print test_image_tpl_string
        test_image_create(test_image_tpl_string=test_image_tpl_string,testimagename = testimagename)
    else:
        pprint(r.text)   
        print "Saturn provisioning error: returned status code %d" %r.status_code
        print "Look at the /var/log/one/oned.log and/or the saturn server log"
        sys.exit(1)


    
    

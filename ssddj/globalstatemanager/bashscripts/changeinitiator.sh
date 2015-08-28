#!/bin/bash
#Copyright 2015 Blackberry Limited
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

set -e
NOS=`sudo scstadmin -list_session | awk "/$1/,/(no sessions)/" | wc -l`
if [ $NOS -eq "3" ]; 
then
        sudo scstadmin -clear_inits -driver iscsi -target $1 -group allowed_ini -noprompt
        sudo scstadmin -add_init $2 -driver iscsi -target $1 -group allowed_ini
        sudo scstadmin -write_config /etc/scst.conf
        echo "ALLOK"$1
        exit 0
else
        echo "FAILURE: Session is up, not changing initiator of $1 to $2"
        exit 1
fi
echo "FAILURE"
exit 1

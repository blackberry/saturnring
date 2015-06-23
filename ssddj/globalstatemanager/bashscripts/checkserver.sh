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

#SCST
sudo service scst status
[ $? -ne 0 ] && echo "FAILURE, SCST not loaded on $HOSTNAME"

#Ping to default GW
DEFAULT_ROUTE=$(ip route show default | awk '/default/ {print $3}')
ping -c 1 $DEFAULT_ROUTE
[ $? -ne 0 ] && echo "FAILURE, PING to default GW $DEFAULT_ROUTE failed on $HOSTNAME"

#Check if necessary packages are installed
#Check if necessary packages are installed
#!/bin/bash
declare -a pkges=( "cryptsetup" "cryptsetup-bin" )
for pkg in "${pkges[@]}"
do
  if [ $(dpkg-query -W -f='${Status}' "$pkg" 2>/dev/null | grep -c "ok installed") -eq 0 ];
  then
    echo "FAILURE, package $pkg not installed on $HOSTNAME"
  fi
done

#All ok
echo "Ok"


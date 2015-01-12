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

#lvs --units g | grep "\s\sthinpool*" | cut -d" " -f6- | tr -d " " | cut -d"g" -f2
#lvs --units g | grep "\s\sthinpool*" | cut -d" " -f6- | tr -d " " | cut -d"g" -f1
#lvdisplay $1/thinpool --units g | grep "Allocated pool data" | sed 's/[^0-9\.]*//g'
#lvdisplay $1/thinpool --units g | grep "LV Size" | sed 's/[^0-9\.]*//g'

#VFree
sudo vgs --noheadings --units g --separator , | cut -d, -f7 | cut -d"g" -f1
#Vsize
sudo vgs --noheadings --units g --separator , | cut -d, -f6 | cut -d"g" -f1

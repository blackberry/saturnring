#!/bin/bash
CAPACITY=`vgdisplay stripedvg | grep "Free  PE / Size" | cut -d'/' -f 3 | cut -d' ' -f 2 |tr -d ' '`
echo $CAPACITY
if [ `echo "$1 < $CAPACITY" | bc` == 1 ]; then
  echo "Capacity available, creating LV"
  lvcreate -i 3 -I 256 storevg -L $1G
else
  echo "Cannot create LV, capacity exceeded"
  exit 1
fi


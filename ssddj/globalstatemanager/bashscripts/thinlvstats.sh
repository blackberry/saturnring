#lvs --units g | grep "\s\sthinpool*" | cut -d" " -f6- | tr -d " " | cut -d"g" -f2
#lvs --units g | grep "\s\sthinpool*" | cut -d" " -f6- | tr -d " " | cut -d"g" -f1
lvdisplay storevg/thinpool --units g | grep "LV Size" | sed 's/[^0-9\.]*//g'
lvdisplay storevg/thinpool --units g | grep "Allocated pool data" | sed 's/[^0-9\.]*//g'


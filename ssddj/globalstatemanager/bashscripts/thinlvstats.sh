lvs --units g | grep "\s\sthinpool*" | cut -d" " -f6- | tr -d " " | cut -d"g" -f2
lvs --units g | grep "\s\sthinpool*" | cut -d" " -f6- | tr -d " " | cut -d"g" -f1

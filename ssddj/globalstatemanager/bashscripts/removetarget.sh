if  python /home/local/saturn/saturn-bashscripts/parsetarget.py | grep $1 | grep "no sessions"
then
        LVOL=`scstadmin -list_target $1  -driver iscsi | grep disk-lvol | cut -d"-" -f2`
        yes | scstadmin -rem_target $1 -driver iscsi
        scstadmin -write_config /etc/scst.conf
        yes | lvremove -f /dev/storevg/$LVOL
else
        echo "Session active, doing nothing"
fi



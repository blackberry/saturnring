from ssdfrontend.models import VG
from ssdfrontend.models import StorageHost
from ssdfrontend.models import LV
from ssdfrontend.models import Target
from django.contrib.auth.models import User
import xlwt
import os
import ConfigParser
import time
import traceback
import logging
def StatMaker():
    logger = logging.getLogger(__name__)
    try:
        BASE_DIR = os.path.dirname(os.path.dirname(__file__))
        config = ConfigParser.RawConfigParser()
        config.read(os.path.join(BASE_DIR,'saturn.ini'))
        book = xlwt.Workbook(encoding="utf-8")
        
        #Summary
        wssum = book.add_sheet('summary')
        wssum.write(0,0,'Summary report for cluster')
        wssum.write(0,1,config.get('saturnring','clustername'))
        wssum.write(1,0,'Report generated at')
        wssum.write(1,1,time.strftime('%c'))
        wssum.write(3,0,'Number of Saturn servers')
        wssum.write(3,1,StorageHost.objects.all().count())
        
        # Storage stats
        wsstorage = book.add_sheet('storage')
        wsstorage.write(0,0,'Saturn host')
        wsstorage.write(0,1,'Total storage (GB)')
        wsstorage.write(0,2,'Allocated (GB)')
        vgs = VG.objects.all()
        vgCtr=0
        totalGB = 0
        allocGB = 0
        for avg in vgs:
            vgCtr=vgCtr+1
            totalGB=totalGB+avg.thintotalGB
            allocGB=allocGB+avg.CurrentAllocGB
            wsstorage.write(vgCtr,0,avg.vghost.dnsname)
            wsstorage.write(vgCtr,1,avg.thintotalGB)
            wsstorage.write(vgCtr,2,avg.CurrentAllocGB)
        wssum.write(4,0,'Total storage (GB)')
        wssum.write(4,1,totalGB)
        wssum.write(5,0,'Used - allocated - storage (GB)')
        wssum.write(5,1,allocGB)
        
        # User stats
        wsusers = book.add_sheet('users')
        tot_sizeinGB = 0
        tot_rkb = 0
        tot_wkb = 0
        quotaGB = 0
        userCtr = 0
        wsusers.write(0,0,'User ID')
        wsusers.write(0,1,'Used GB')
        wsusers.write(0,2,'Quota GB')
        wsusers.write(0,3,'Read KB')
        wsusers.write(0,4,'Written KB')
        users = User.objects.all()
        for aUser in users:
            try:
                tot_sizeinGB = 0
                tot_rkb = 0
                tot_wkb = 0
                userTargets = Target.objects.filter(owner=aUser)
                userCtr = userCtr+1
                for eachTarget in userTargets:
                    tot_sizeinGB = tot_sizeinGB + eachTarget.sizeinGB
                    tot_rkb = tot_rkb + eachTarget.rkb
                    tot_wkb = tot_wkb + eachTarget.wkb
                quotaGB = quotaGB+aUser.profile.max_alloc_sizeGB
                wsusers.write(userCtr,0,aUser.username)
                wsusers.write(userCtr,1,tot_sizeinGB)
                wsusers.write(userCtr,2,aUser.profile.max_alloc_sizeGB)
                wsusers.write(userCtr,3,tot_rkb)
                wsusers.write(userCtr,4,tot_wkb)
            except:
                var = traceback.format_exc()
                logger.warn("User stat error: %s" %(var,))

        wssum.write(6,0,'Quota (promised) GB')
        wssum.write(6,1,quotaGB)
        wssum.write(7,0,'Number of users')
        wssum.write(7,1,userCtr)
        #
        dir = config.get('saturnring','iscsiconfigdir')
        fileName = config.get('saturnring','clustername')+'.xls'
        try:
            os.remove(os.path.join(dir,fileName)) #old file
        except:
            logger.info("Tried to delete non-existent stat file")
        logger.info("Saving stat file to %s" % (os.path.join(dir,fileName),))
        book.save(os.path.join(dir,fileName))
        return 0
    except:
        var = traceback.format_exc()
        logger.warn("Stat generation (XLS) error: %s" %(var,))
        return 1

if __name__=='__main__':
    stat = StatInfo()

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
logger = logging.getLogger(__name__)
class StatInfo:
    def __init__(self):
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
            userCtr = 0
            wsusers.write(0,0,'User ID')
            wsusers.write(0,1,'GB')
            wsusers.write(0,2,'Read KB')
            wsusers.write(0,3,'Written KB')
            users = User.objects.all()
            for aUser in users:
                userTargets = Target.objects.filter(owner=aUser)
                userCtr = userCtr+1
                for eachTarget in userTargets:
                    tot_sizeinGB = tot_sizeinGB + eachTarget.sizeinGB
                    tot_rkb = tot_rkb + eachTarget.rkb
                    tot_wkb = tot_wkb + eachTarget.wkb
                wsusers.write(userCtr,0,aUser.username)
                wsusers.write(userCtr,1,tot_sizeinGB)
                wsusers.write(userCtr,2,tot_rkb)
                wsusers.write(userCtr,3,tot_wkb)
            wssum.write(6,0,'Number of users')
            wssum.write(6,1,userCtr)
            #
            dir = config.get('saturnring','iscsiconfigdir')
            fileName = config.get('saturnring','clustername')+'.xls'
            logger.info('Writing out stat file %s' % (fileName))
            book.save(os.path.join(dir,fileName))
        except:
            var = traceback.format_exc()
            logger.warn("Stat generation (XLS) error: %s" %(var,))

if __name__=='__main__':
    stat = StatInfo()

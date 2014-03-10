#import the Fabric api
from fabric.api import *

# We can then specify host(s) and run the same commands across those systems
env.user = 'vagrant'
env.password = 'vagrant'
env.hosts = ['192.168.61.20']

def uptime():
        run("uptime")

def pvscan():
        run("sudo pvscan")

def installScripts():
    run("mkdir -p  bashscripts")
    put("bashscripts/*.*","bashscripts")
    run("chmod 755 bashscripts/*.*")
def makeLUN(lunSizeGB):
	run(" ".join(["sudo bashscripts/createlun.sh",lunSizeGB]))



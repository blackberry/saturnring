#!/bin/bash
#Name of Saturnring cluster
CLUSTERNAME=saturndevcluster
#Django secret key
#Its a bad idea to use sqllite in production, because the locking mechanism doesnt work so when there are multiple requests to Saturnring things
#wont work quite well. Use Postgres or MariaDB or Oracle instead.
DATABASE_TYPE=sqlite
DATABASE_NAME=saturntestdb.sqlite
#N/A for non-SQLLite DB
DATABASE_DIR=/home/vagrant/sqlitedbdir
#N/A for SQLlite DB
DATABASE_HOST=dbhost
#Only applicable for POstgres
DATABASE_PORT=5432
#Only applicable for POstgres
DATABASE_USER=postgres
#Only applicable for POstgres,N/A for sqlite
DATABASE_PASSWORD=postgres
DJANGOSECRETKEY=pleasechangemeinproduction
#User account on saturnringserver 
LDAP_ENABLED=0
LDAP_LDAP_URI=ldap://ldapserver.url
LDAP_USER_DN="=OU=Users,OU=Ring,OU=ouname,DC=ad0,DC=dcname"
LDAP_STAFF_GROUP="CN=Cloud Customers,OU-Security Groups, DC=ad0,DC=dcname"
LDAP_BIND_USER_DN="ldapreadaccount,CN=Users,DC=ad0,DC=dcname"
LDAP_BIND_USER_PW=sup3rs3cur3
NUMWORKERS=3
SATURNWKDIR=/nfsmount/saturnring
SATURNRINGHOST=192.168.61.20
SATURNRINGAPACHEPORT=80
INSTALLUSER=vagrant
INSTALLLOCATION=/vagrant
CODEROOT=/vagrant
SATURNRINGPASSWORD=changeme
ADMINEMAIL=admin@changeme.org
PROXYFOLDER=''

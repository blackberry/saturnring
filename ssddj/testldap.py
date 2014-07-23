import ldap
import ConfigParser
import traceback
import os
import pprint
ldap.set_option(ldap.OPT_REFERRALS, 0)
config = ConfigParser.RawConfigParser()
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
print str(BASE_DIR)
config.read(os.path.join(BASE_DIR,'saturn.ini'))

l = ldap.initialize(config.get('activedirectory','ldap_uri'))
ldap.set_option(ldap.OPT_DEBUG_LEVEL, 4095)
try:
    l.protocol_version = ldap.VERSION3
    l.set_option(ldap.OPT_REFERRALS, 0)
    bind = l.simple_bind_s("ldapreader","ld@pr3ad3r!")
    #bind = l.simple_bind_s()
    base = config.get('activedirectory','user_dn').strip('"')
    print base
    #criteria = "(&(objectClass=user)(sAMAccountName=username))"
    #attributes = ['displayName', 'company']
    result = l.search_s(base, ldap.SCOPE_SUBTREE)

    results = [entry for dn, entry in result if isinstance(entry, dict)]
    pprint.pprint( results )
except:
    var = traceback.format_exc()
    print var

finally:
    l.unbind()


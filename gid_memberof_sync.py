import sys, subprocess, ldap

from ldap import modlist
ldap.set_option(ldap.OPT_REFERRALS, 0)

ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)

LDAP_SERVER = 'ldaps://000.000.000.000:636'
AD_BIND_UPN = ''
AD_BIND_PW = ''
DOMAIN_STRING = ''
USER_BASE_DOMAIN = 'ou=Domain Users,dc=rc,dc=domain'
GROUP_BASE_DOMAIN = 'dc=rc,dc=domain'

class LDAPConnection:
    #connect to the server
    def __init__(self, ldap_server=LDAP_SERVER):
        self.conn = ldap.initialize(ldap_server)
        self.conn.simple_bind_s(AD_BIND_UPN, AD_BIND_PW)
    def unbind(self):
        if not self.conn:
            return
        self.conn.unbind_s()
    def add_group_member(self, user_dn, group_dn_result):
	self.conn.modify_s(group_dn_result,[(ldap.MOD_ADD, "member", user_dn)])
    def get_user_attr(self, username):
	dn, member_of, gid_number = False, False, False
	if username == "*":
	    filter = '(&(objectClass=user)(objectCategory=person))'
            result = self.conn.search_ext_s(USER_BASE_DOMAIN, ldap.SCOPE_SUBTREE, filter, ['*'])
	    count = 0
	    for r in result:
		if 'memberOf' in r[1]:
			uac = r[1]['userAccountControl']
			uac = int(uac[0])
			if uac == 514 or uac == 546 or uac == 66050 or uac == 65538 or uac == 8388608 or uac == 8388610:
			    print "\nThis account is disabled %s has uac of %s\n" %(r[1]['cn'],uac) 
			    continue
			member_of = r[1]['memberOf']
                	gid_number = r[1]['gidNumber'][0]
                	user_dn = r[1]['distinguishedName']
	    		#print "%s\n%s\n%s\n" %(user_dn, member_of, gid_number)
			do_check_and_add(user_dn, member_of, gid_number)
			count = count + 1
			#if count == 200:
			#    sys.exit() 
	else:
	   filter = '(&(objectClass=person)(sAMAccountName=%s))' % username
           result = self.conn.search_ext_s(USER_BASE_DOMAIN, ldap.SCOPE_SUBTREE, filter, ['*'])
        if not result:
        	print "No matching username"
        	sys.exit()
        if 'memberOf' in result[0][1]: 
		member_of = result[0][1]['memberOf']
		gid_number = result[0][1]['gidNumber'][0]
		user_dn = result[0][1]['distinguishedName']
		do_check_and_add(user_dn, member_of, gid_number) 
    def get_group_gid(self, group_dn):
	filter = '(&(objectClass=group)(distinguishedName=%s))' % group_dn
	result = self.conn.search_ext_s(GROUP_BASE_DOMAIN, ldap.SCOPE_SUBTREE, filter, ['*'])
	gid_result = False
        group_dn_result =False
	if not result:
		return (group_dn_result, gid_result)
	if 'gidNumber' in result[0][1]:
		gid_result = result[0][1]['gidNumber'][0]
		group_dn_result = result[0][1]['distinguishedName']
		#print group_dn_result
	return (group_dn_result, gid_result)
    def get_group_dn(self, gid_number):
	filter = '(&(objectClass=Group)(gidNumber=%d))' %(int(gid_number))
        result = self.conn.search_ext_s(GROUP_BASE_DOMAIN, ldap.SCOPE_SUBTREE, filter, ['*'])
	group_dn = False
	if result:
		group_dn = result[0][1]['distinguishedName']
	return (group_dn[0])

def do_check_and_add(user_dn, member_of, gid_number):
    #print "\nchecking...\n%s====>\n" %user_dn

    #count = 0 
    for group_dn in member_of:
	#count += 1 
	#print "|%d| %s" %(count,group_dn) 
	group_dn_result, gid_result = conn.get_group_gid(group_dn)
	#print "%s\n%s\n" %(group_dn_result, gid_result)
	if gid_result == False:
	   pass 
	   #print "This is an invalid group: %s" %group_dn
	if gid_result == gid_number: 
	    #print "You arleady are a member of your primary unix group\n====================================================\n%s\n%s\n%s=%s" %(user_dn[0],group_dn_result[0],gid_result,gid_number)
	    return
    print "You are not a member of your Unix group, I will add you now..."

    print "searching %s" %gid_number
    group_dn = conn.get_group_dn(gid_number)
    try:
        conn.add_group_member(user_dn[0], group_dn)
        print "member %s has been added to group %s" %(user_dn[0],group_dn)
    except ldap.ALREADY_EXISTS:
        print "User %s already exists in group %s" %(user_dn[0],group_dn)
    except ldap.LDAPError, error_message:
        print "Error setting password: %s" % error_message

sys.stdout = open('gid_to_memberof.log', 'w')
conn = LDAPConnection()
#user_dn, member_of, gid_number = conn.get_user_attr('lsilva')
list = conn.get_user_attr('*')
print list
conn.unbind()

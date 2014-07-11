# Script is designed to dump the email addresses of all cluster users
# This will ensure that AD is synced with the Hptc-users-list.lists.fas.harvard.edu 
# mailman list. 
# Written by: Luis Silva 04/13/2012
#
import os,ldap
def get_ldap_connection(): #funtion for binding to AD via LDAP
    """
    Bind to server, return connection
    """
    #set up ldap connection
    server='' # server IP
    who='' # dn of AD user
    cred='' # password of AD user
    print 'pre-open'
    l=ldap.open(server)
    print 'post-open'
    l.protocol_version = 3 
    l.simple_bind_s(who,cred)
    print "Successfully Bound to server.\n"
    return l
def get_email_address(username): # function that searches AD for a users and returns thier principal email address
	global LDAP_CONN
	ldap_conn = LDAP_CONN
	base ='ou=Domain Users,dc=rc,dc=domain'
	cgrbase='ou=CGR,dc=rc,dc=domain'
	scope = ldap.SCOPE_SUBTREE
	ldap_filter = '(&(objectClass=person)(sAMAccountName=%s))' %(username)
	attrs = ['mail']
	scrhArray = []
	rcsrch = ldap_conn.search_ext_s(base,scope,ldap_filter,attrs)
	cgrsrch = ldap_conn.search_ext_s(cgrbase,scope,ldap_filter,attrs)
	srchArray = [rcsrch,cgrsrch]
	srch_results_mail = 'null'
	for srch in srchArray:
		for dn,keys in srch:
			if keys.has_key('mail'):
				srch_results_mail = keys['mail'][0]
				print srch_results_mail
	return srch_results_mail
def get_status(username): # function that searches AD for the user and returns thier User Account Control attribute
	global LDAP_CONN
	ldap_conn = LDAP_CONN
	base ='ou=Domain Users,dc=rc,dc=domain'
	cgrbase='ou=CGR,dc=rc,dc=domain'
	scope = ldap.SCOPE_SUBTREE
	ldap_filter = '(&(objectClass=person)(sAMAccountName=%s))' %(username)
	attrs = ['userAccountControl']
	scrhArray = []
	rcsrch = ldap_conn.search_ext_s(base,scope,ldap_filter,attrs)
	cgrsrch = ldap_conn.search_ext_s(cgrbase,scope,ldap_filter,attrs)
	srchArray = [rcsrch,cgrsrch]
	srch_results_status = 'null'
	for srch in srchArray:
		for dn,keys in srch:
			if keys.has_key('userAccountControl'):
				srch_results_status = keys['userAccountControl'][0]
				print srch_results_status
	return srch_results_status

if __name__=='__main__':
	LDAP_CONN = get_ldap_connection() # binds to LDAP
	os.system("getent passwd |grep -e '/n/home[00-13]' -e '/users'>datafile.txt") #dumps grep search to file for parsing later
	reader=open("datafile.txt") # opens data file for reading
	f = open('emaildump.txt', 'w') # opens file where all the valid email address will go later
	nadafile = open('noemailaddy.txt', 'w') # Opens file where users with no email attributes fullname will be stored
	for lines in reader.readlines(): # loop through the file with the ldap query data in it
		#print lines
		linearray=[] # throwing everthing in an array
		linearray.append(lines.split(":")) # splitting on the colon becuase that how getent outputs stuff
		for username,w,uid,gid,fullname,homedir,shell in linearray: # looping through while assigning a variable to all the attributes
			print username
			uac=get_status(username)
			if uac == '512'or uac == '66048':
				if get_email_address(username) == 'null':
					print "This user has no email address: %s" %fullname
					nadafile.write("%s\n" %fullname)
				else:	
					print "this user has an active account... writing out to emaildump.txt"
					f.write("%s\n" %get_email_address(username))
			elif uac == '514':
				print "### This is a disabled account ###"
	f.close()
	nadafile.close()
		

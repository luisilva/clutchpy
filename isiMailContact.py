#!/usr/bin/python

# Author Luis Silva 01-14-2015

## used for gathering contact information for the multiple shares on the isilon
## by getting the gid's at the first and second layer of the directoires then querying AD
## for those group member and thier email addresses.

# This should be run on sa01 as it has access to both isilon systems


import os,sys,string,sh,ldap
from stat import *

# Setting this gobal value for the top level directory in both isilons all shares are
# at the next level.
rootifs=["/net/rcstore/ifs/rc_labs/", "/net/rcstore02/ifs/rc_labs/"] 

def get_share_names(rootifs):
    rc_lab_share_info =[]
    for isi in rootifs:
        #rc_lab_dirs.append(sh.ls(isi))
        for directory in sh.ls(isi).split():
            share_dict = {'top': isi,'name':directory}
            rc_lab_share_info.append(share_dict)
    return rc_lab_share_info

#grabs subdirectory gids of parent share, just need one layer here in case root share is not useful.
def get_next_level(fullpath):
    gidlist =[]
    for f in os.listdir(fullpath):
        subdirpath = os.path.join(fullpath,f)
        if os.path.islink(subdirpath):
            continue
        else:
            mode = os.stat(subdirpath).st_mode
        if ".snapshot" in subdirpath:
            continue
        elif S_ISLNK(mode):
            print "yes!!!"
        elif S_ISDIR(mode):
            gidlist.append(os.stat(subdirpath).st_gid)
        else:
            continue
    return gidlist
    
# Grab the GID from the share level directory and calls function to grab subdirectories gids
def get_groups_per_share(item):
    gidlist =[]
    #print "checking share %s" %item['name']
    fullpath = os.path.join(item['top'],item['name'])
    gidlist.append(get_next_level(fullpath))
    gidlist.append(os.stat(fullpath).st_gid)
    return gidlist
    
#This flattens the list so that there aren't lists of list. 
def flatten(lst):
    for elem in lst:
        if type(elem) in (tuple, list):
            for i in flatten(elem):
                yield i
        else:
            yield elem
            
# clear remove local gids 0-1000
def remove_local_gids(uniqueflattesortednList):
    blacklist = range(0,1001)
    myList = [e for e in uniqueflattesortednList if int(e) not in blacklist]
    return myList
    
####### LDAP Stuff #########
def get_ldap_connection():
    """
    Bind to server, return connection
    """
    #set up ldap connection
    server=''
    who=''
    cred=''
    print 'pre-open'
    l=ldap.open(server)
    print 'post-open'
    l.protocol_version = 3
    l.simple_bind_s(who,cred)
    print "Successfully Bound to server.\n"
    #print l
    return l

def get_ldap_group_obj(groupname):
    global LDAP_CONN
    email_srch_result= []
    """ Searches, bases on the cn"""
    base ='ou=Domain Groups,dc=rc,dc=domain'
    scope = ldap.SCOPE_SUBTREE
    ldap_filter = 'gidNumber=%s' % groupname
    #attrs = ['*']
    attrs = ['member']
    print ldap_filter
    srch_results = LDAP_CONN.search_ext_s(base,scope,ldap_filter,attrs)
    for userDN in srch_results:
        if 'member' in userDN[1]:
            for member in userDN[1]['member']:
                email_srch_result = get_ldap_user_obj(member)
    return email_srch_result
    
LDAP_QUERY_CNT = 0
EMAIL_LOOKUP_CNT =0
USER_EMAIL_LOOKUP = {}	# { userDN : email }
def get_ldap_user_obj(userDN):
    global USER_EMAIL_LOOKUP, EMAIL_LOOKUP_CNT
    EMAIL_LOOKUP_CNT +=1
    if USER_EMAIL_LOOKUP.has_key(userDN):
         return USER_EMAIL_LOOKUP.get(userDN, None)

    """ Searches, bases on the dn"""
    global LDAP_CONN, LDAP_QUERY_CNT
    ldap_conn = LDAP_CONN
    base ='ou=Domain Users,dc=rc,dc=domain'
    cgrbase='ou=CGR,dc=rc,dc=domain'
	#Old OU's that have been moved into Domain Users
    #mcbbase='ou=MCB,dc=rc,dc=domain'
    #oebbase='ou=OEB,dc=rc,dc=domain'
    #ccbbase='ou=ccb,dc=rc,dc=domain'
    #cnsbase='ou=CNS,dc=rc,dc=domain'
    scope = ldap.SCOPE_SUBTREE
    #ldap_filter = '(&(objectCategory=person)(objectClass=User))' 
    ldap_filter = '(&(objectClass=person)(distinguishedName=%s))' % userDN
    print ldap_filter
    attrs = ['distinguishedName', 'mail']
    scrhArray = []
    
    seersrch = ldap_conn.search_ext_s(base,scope,ldap_filter,attrs)
    cgrsrch = ldap_conn.search_ext_s(cgrbase,scope,ldap_filter,attrs)
    
    srchArray = [seersrch,cgrsrch]
    srch_results = 'null'
    for srch in srchArray:
    	#print '>> using srch', srch
	for dn, keys in srch:
		if (dn == userDN):
			if keys.has_key('mail'):
				srch_results = keys['mail']
			        LDAP_QUERY_CNT+=1		
    				USER_EMAIL_LOOKUP.update({userDN:srch_results})
	   			#msg('(%s) Found! %s' % (LDAP_QUERY_CNT, keys['mail']))
			else:
    				USER_EMAIL_LOOKUP.update({userDN:None})
    return srch_results

if __name__=='__main__':
    ## asumptions all things are under /net/rcstore[|02]/ifs/[rc_admin|rc_labs]
    LDAP_CONN = get_ldap_connection()
    for item in get_share_names(rootifs):
        complete_gid_list = get_groups_per_share(item)
        flattenedList = list(flatten(complete_gid_list))
        flattenedList = [int(x) for x in flattenedList]
        uniqueflattesortednList = set(sorted(flattenedList))
        cleanlist = remove_local_gids(uniqueflattesortednList)
        for obj in cleanlist:
            print get_ldap_group_obj(obj)
        #print "The ID's for %s are:\n %s" %(item['name'],cleanlist)
        

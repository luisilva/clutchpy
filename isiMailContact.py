#!/usr/bin/python

# Author Luis Silva 01-14-2015

## used for gathering contact information for the multiple shares on the isilon
## by getting the gid's at the first and second layer of the directoires then querying AD
## for those group member and thier email addresses.

# This should be run on sa01 as it has access to both isilon systems


import os,sys,string,sh,ldap
from stat import *
from pyad import *

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
    who='cn=groupsync,ou=Unmanaged Service Accounts,dc=rc,dc=domain'
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
    """ Searches, bases on the cn"""
    base ='ou=Lab_Instruments,ou=Domain Groups,ou=CGR,dc=rc,dc=domain'
    scope = ldap.SCOPE_SUBTREE
    ldap_filter = 'sAMAccountName=%s' % groupname
    attrs = ['*']
    # print ldap_filter
    srch_results = LDAP_CONN.search_ext_s(base,scope,ldap_filter,attrs)
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
        

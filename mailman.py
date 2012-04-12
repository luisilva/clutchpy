# This is for sycing email addresses from all the "G_" groups
# in the RC domain to matching "G_" groups in mailman.
#
# Author Luis Silva 06-13-2011
 
import os,sys,string,ldap
from datetime import datetime
import time
 
def msg(m): print m
def dashes(): print '-' * 40
def msgt2(m): msg('>> %s' % m)
def msgt(m): dashes(); msg(m); dashes()
def msgx(m): msgt(m); sys.exit(0)
 
# Deifnes who is the list manager and the defaultPw for all the lists.
adminEmail = ''
defaultPw = ''
mailmanCmdLocation = '/usr/lib/mailman/bin/'
pwd = '/mailmanSync/groupSync/temp_files'
 
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
 
LDAP_CONN = get_ldap_connection() 
 
def get_ldap_group_obj( groupname):
    global LDAP_CONN
    """ Searches, bases on the cn"""
    base ='ou=Lab_Instruments,ou=Domain Groups,ou=CGR,dc=rc,dc=domain'
    scope = ldap.SCOPE_SUBTREE
    ldap_filter = 'sAMAccountName=%s' % groupname
    attrs = ['*']
   # print ldap_filter
    srch_results = LDAP_CONN.search_ext_s(base,scope,ldap_filter,attrs)
    return srch_results
 
LDAP_QUERY_CNT = 0
EMAIL_LOOKUP_CNT =0
"""
Need to fix this for efficiency, not to run hundreds of queries
"""
USER_EMAIL_LOOKUP = {}  # { userDN : email }
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
    attrs = ['distinguishedName', 'mail']
    scrhArray = []
 
    seersrch = ldap_conn.search_ext_s(base,scope,ldap_filter,attrs)
    cgrsrch = ldap_conn.search_ext_s(cgrbase,scope,ldap_filter,attrs)
    #mcbsrch = ldap_conn.search_ext_s(mcbbase,scope,ldap_filter,attrs)
    #oebsrch = ldap_conn.search_ext_s(oebbase,scope,ldap_filter,attrs)
    #ccbsrch = ldap_conn.search_ext_s(ccbbase,scope,ldap_filter,attrs)
    #cnssrch = ldap_conn.search_ext_s(cnsbase,scope,ldap_filter,attrs)
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
 
def start_mailman_sync():
 
    global noEmailDNList
    noEmailDNList = []
    groupname = '*' #_test'
    groupObj = get_ldap_group_obj(groupname)
 
    rcGroupArray =[]
    for a,b in groupObj:
        rcGroupArray.append(b['sAMAccountName'])
        print b["sAMAccountName"]
 
    #print rcGroupArray
    msg('# of AD groups to check: %s' %  len(rcGroupArray))
 
    mailmanLists = os.popen(mailmanCmdLocation +'/list_lists -b').readlines()
 
    #print mailmanLists
    msg('# of mailman groups to check: %s' %  len(mailmanLists))
    reconcile_mailmain_lists(mailmanLists, rcGroupArray)
 
def get_member_emails_from_group(groupname):
    msgt2('get_member_emails_from_group: %s' % groupname)
    if groupname is None:
        return []
 
        groupObj =get_ldap_group_obj( groupname)
        rcMemberArray =[]
        for c,d in groupObj:
        if d.has_key('member'):
            for mem in d['member']:
                #print mem
                userDN = mem
                userMail = get_ldap_user_obj(userDN)
                                #get_ldap_user_obj('CN=Kunal Tiwari,OU=SEER,OU=Domain Users,DC=rc,DC=domain')
                #print userMail[0]
                if userMail is not None:
                    rcMemberArray.append(userMail[0])
                else:
                    noEmailDNList.append(userDN)
 
    rcMemberArray = filter(lambda x: x is not None and len(str(x)) >= 3, rcMemberArray)
    rcMemberArray.sort()
    return rcMemberArray
 
def get_mailman_list_members(list_name):
        msgt2('get_mailman_list_members: %s' % list_name)
 
        if list_name is None:
        return []
    str_get_members_cmd = '%slist_members %s' % (mailmanCmdLocation, list_name)
    mailman_members = os.popen(str_get_members_cmd).readlines()
        mailman_members = map(lambda x: x.strip(), mailman_members)
        return mailman_members
 
def pause():
    nsec =0 #1
    msg('%s second pause' % nsec)
    time.sleep(nsec)
 
def read_temp_file(fname):
    msg('open file: %s' % fname)
    fh = open(fname, 'r')
    flines = fh.readlines()
    fh.close()
    return flines
 
def write_temp_file(fcontent, fname):
    msg('write file: %s' % fname)
    fh = open(fname, 'w')
    fh.write(fcontent)
    fh.close()
    pause()
 
def get_temp_filename(file_prefix='temp'):
    now = datetime.now()
    return os.path.join(pwd, '%s_%s%s.txt' % (file_prefix, now.strftime('%m-%d-%Y_%I-%M-%S'), now.microsecond))
 
def remove_extra_members_from_mailman(groupname, mailman_members_to_remove):
        msgt2('remove_extra_members_from_mailman: [%s][%s]' % (groupname, mailman_members_to_remove))
 
        if groupname is None or mailman_members_to_remove is None or len(mailman_members_to_remove) == 0:
                return
    fname = get_temp_filename(groupname)
    write_temp_file('\n'.join(mailman_members_to_remove), fname)
        msg('file written')
 
    str_remove_members = '%sremove_members -f %s %s' % (mailmanCmdLocation,fname,groupname)
        msg('mailman cmd: [%s]' % str_remove_members)
        os.system(str_remove_members)
        #os.popen(str_remove_members)
        msg('mailman command executed')
 
def add_members_to_mailman_list(groupname, new_mailman_members):
    msgt2('add_members_to_mailman_list: [%s][%s]' % (groupname, new_mailman_members))
 
    if groupname is None or new_mailman_members is None or len(new_mailman_members) == 0:
        return
        fname = get_temp_filename(groupname)
    write_temp_file('\n'.join(new_mailman_members), fname)
    msg('file written')
 
    str_add_members = '%sadd_members -r %s %s' % (mailmanCmdLocation,fname,groupname)
    msg('mailman cmd: [%s]' % str_add_members)
    os.system(str_add_members)
    #os.popen(str_add_members)
    msg('mailman command executed')
 
def make_new_mailman_list_and_populate(groupname):
    msgt2('make_new_mailman_list_and_populate: %s' % groupname)
    strNewlist = '%snewlist -q %s %s %s' %(mailmanCmdLocation,groupname,adminEmail,defaultPw)
    print strNewlist
    os.system(strNewlist)
    #os.popen(strNewlist)
    msgt2('New list created: %s' % groupname)
 
    rcMemberArray = get_member_emails_from_group(groupname)
    print rcMemberArray
    print len(rcMemberArray)
        print '\n'.join(rcMemberArray)
 
        fname = get_temp_filename(groupname)
        write_temp_file('\n'.join(rcMemberArray), fname)
    strAddMem = '%sadd_members -r %s %s' %(mailmanCmdLocation, fname,groupname)
        print strAddMem
        os.system(strAddMem)
    #os.popen(strAddMem)
    #subprocess.call(strAddMem.split())
def lower_and_strip_list(lst):
    lst = map(lambda x: x.lower().strip(), lst)
        return filter(lambda x: len(x) > 0, lst)
 
def reconcile_mailmain_lists(mailmanLists, rcGroupArray):
    msgt('reconcile_mailmain_lists')
    if mailmanLists is None or rcGroupArray is None:
        print 'reconcile_mailmain_lists: No lists to reconcile'
        return
    loop_counter =0
    really_sync = False
    for rcItem in rcGroupArray:
        loop_counter +=1
        ad_group_name= rcItem[0].strip()
                msg('')
        msgt('(%s) check list: %s' % (loop_counter, ad_group_name))
        print 'lookup size: %s' % len(USER_EMAIL_LOOKUP)
        print 'email lookups: %s' % EMAIL_LOOKUP_CNT
        itemExists = False
        for mailmanItem in mailmanLists:
            rc = ad_group_name.lower()
            man = mailmanItem.lower().strip()
 
            if (rc == man):
                print 'AD group matches Mailman group name'
                itemExists = True
                break
        #print itemExists
        if loop_counter >= 0:    #ad_group_name == 'G_AWM_Inverted':
            really_sync=True
                else:
                    really_sync=False
        if really_sync:
                        if ad_group_name.find(' ') > -1:
                    msgx('spaces found in AD name: [%s]' % ad_group_name)
 
            elif not itemExists:
                #msgt('make_new_mailman_list_and_populate: %s' % rcItem[0])
                make_new_mailman_list_and_populate(ad_group_name)
 
            elif itemExists:
                msgt('reconcile lists: %s' % ad_group_name)
 
                # retrieve/format AD group email addresses
                rcMemberArray = get_member_emails_from_group(ad_group_name)
                rcMemberArray = lower_and_strip_list(rcMemberArray)
 
                # retrieve/format mailman email addresses
                list_members = get_mailman_list_members(ad_group_name)
                list_members = lower_and_strip_list(list_members)
 
                # add missing members to mailman
                new_mailman_members = []
                for ad_email in rcMemberArray:
                    if not ad_email in list_members:
                        new_mailman_members.append(ad_email)
                if len(new_mailman_members) > 0:
                    add_members_to_mailman_list(ad_group_name, new_mailman_members)
 
                # remove extra members from mailman
                mailman_members_to_remove = []
                for mm_email in list_members:
                    if not mm_email in rcMemberArray:
                        mailman_members_to_remove.append(mm_email)
                if len(mailman_members_to_remove) > 0:
                    remove_extra_members_from_mailman(ad_group_name, mailman_members_to_remove)
 
                if len(mailman_members_to_remove) == 0 and len(new_mailman_members)==0:
                    msg('groups are the same')
                else:
                    msg('> groups reconciled')
                    dashes()
                    print 'rcMemberArray',get_member_emails_from_group(ad_group_name)
                    dashes()
                    print 'list_members', get_mailman_list_members(ad_group_name)
                        #if ad_group_name == 'G_ABI7900': msgx('exit')
 
def remove_temp_files():
    msgt('remove temp files')
    global pwd
    fcnt =0
    for fname in os.listdir(pwd):
        fullpath = os.path.join(pwd, fname)
        if os.path.isfile(fullpath) and fname.endswith('.txt'):
            os.remove(fullpath)
            print 'temp file removed: %s' % fullpath
            fcnt+=1
    msg('# files deleted: %s' % fcnt)
 
def delete_test_mailman_list():
    os.popen('/usr/lib/mailman/bin/rmlist G_ABI7900')
    print 'list deleted'
 
#delete_test_mailman_list()
 
def write_noEmail_file():
    f = open('/mailmanSync/groupSync/noEmailList.txt','w')
    output = []
    for DNs in noEmailDNList:
        if DNs not in output:
            output.append(DNs)
    for uniqueDNs in output:
        f.write('%s\n' % uniqueDNs)
 
    f.close()
 
if __name__=='__main__':
    #delete_test_mailman_list()
    start_mailman_sync()
    remove_temp_files()
    write_noEmail_file()
# Written by: Luis Slva
# Date: 08-21-2011
#
# The srcipt is designed to be run in cron in order to backup the databases on any given mysql machine.
# It will first list the databases then do a mysqldump on each database individually and compress the output to a file share. 
#
import os
import os.path
from datetime import datetime, timedelta, date
#
# All perameters are set by editing these values: 
#
mysqlServer = "" 				#FQDN of your mysql server (localhost works too)
mysqlUser = "" 					# username that has access usually root
accessGroup = "" 				# group that you would like the zip files owned by
pwFile = "" 					# make a file with the password as the first line in it and lock it down
mysqlPwd = open(pwFile, 'r').read().strip() 	# Read that file in here
backupDir = "" 					# the directory that all the backups will go in
#
# Code starts here!: 
#
# setting some variables here
now = str(datetime.now()) # These are of type datetime 
wkAgo = datetime.now() - timedelta(days=7) # type datatime again
strWkAgo = str(datetime.now() - timedelta(days=7)) # I need to convert the week ago date to a string so I can match on it later
nowFormatted = now.split(" ")[0] # getting just the date splitting off the time
wkAgoFormatted = strWkAgo.split(" ")[0] # getting just the date splitting off the time
#
# extracts the date from the file name
def get_file_date(fileName): 
	strFileDate = fileName.split('.')[1]
	return datetime.strptime(strFileDate,"%Y-%m-%d")
#
# executes what ever mysql command you give it.
def execute_mysqlCommand(cmd):
	return os.popen(('mysql -h %s -u %s -p%s -e "%s;"') %(mysqlServer,mysqlUser,mysqlPwd,cmd)) 
#
# runs a mysqldump on what ever database name you give it.
def execute_mysqlDump(dbName):
	dumpString = (('mysqldump -h %s -u %s -p%s %s > %sDATABASE-%s.%s.sql') %(mysqlServer,mysqlUser,mysqlPwd,dbName,backupDir,dbName,nowFormatted))
	print dumpString
	return os.popen(dumpString) 
def zipAll():
	os.popen('tar -czvf  %sDATABASE-ALL.%s.sql.tgz %s%s' %(backupDir,nowFormatted,backupDir,zipString))
	return
#
#
dblist = execute_mysqlCommand("show databases")

print execute_mysqlCommand("FLUSH TABLES WITH READ LOCK")
first = "True"
for dbName in dblist: # Loops through all the databases names
	if first == True:
		first = "Flase"
	elif dbName.strip() == "Database":
		print "skipping title"
	else:
		dbName = dbName.strip()
		print "atempting to create: " + dbName
		execute_mysqlDump(dbName)
		print dbName + " successfully completed" 

print execute_mysqlCommand("UNLOCK TABLES")

# read backup directory and delete files older that 7 days
def get_attribs():
	bkpFiles = os.popen(('ls -lh %s') %(backupDir))
	attribs= []
	first = True
	for files in bkpFiles:
		if first:
			print "skipping first line:" 
			first = False
		else:
			print files.split()
			attribs.append(files.split()[8])
	return attribs

bkpDirList = get_attribs()
print bkpDirList
for fileName in bkpDirList:	
	FileDate = get_file_date(fileName)
	if FileDate > wkAgo:
		print "kept: " + fileName
	else:
		os.popen(('rm -fv %s%s') %(backupDir, fileName))
		print "deleted: " + fileName
#
# building zip of all databases
zipString = "*.sql"
zipAll()
# delete all the sql files left behind
os.popen(('rm -fv %s*.sql') %(backupDir)) 

#set permissions so that database admins can use these for data recovery
os.popen(('chown -R root:%s %s') %(accessGroup,backupDir))
os.popen(('chmod -R 770 %s') %(backupDir))

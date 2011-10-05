# Written by: Luis Silva
# Date 10-04-2011
#
# 1. Makes homedirectory for a new user in /n/ncfusers/<username>
# 2. Copies defualt configuration data into there new home directory /n/ncfusers/default-profile/ => /n/ncfusers/<username>
#
from subprocess import Popen, PIPE
import sys
# constants
defaultConfPath = "/n/ncfusers/default-profile/"
homeDirPath = "/n/ncfusers/"

# Test to make user that thier are 2 arguments ahead of the command. 
def testArgs():
	count = 0 
	for arg in sys.argv:
		count += 1
		if count == 2:
			username = arg
		elif count == 3:
			groupname = arg	
	if count < 3:
		sys.exit("not enough arguments!\nPlease user the propper syntax:\npython mk-ncfhomedir.py <username> <group>")
	elif count > 3:
		sys.exit("too many arguments!\nPlease user the propper syntax:\npython mk-ncfhomedir.py <username> <group>")
	return (username, groupname)

# Run Test and get variables
username, groupname = testArgs()

# Make new home directory
dirPath = homeDirPath + username

makedir = Popen(['mkdir', dirPath], stdout=PIPE, stderr=PIPE)
mkOutput = makedir.stdout.read()
mkError = makedir.stderr.read()

if mkOutput == "" and mkError == "" :
	print "Home directory created: " + dirPath
else:
	print "Output: " + mkOutput
	print "Error: "+ mkError

# copy data from default directory. 

cpData = Popen(['rsync','-av', defaultConfPath, dirPath], stdout = PIPE, stderr=PIPE)
cpOutput = cpData.stdout.read()
cpError = cpData.stderr.read()

if cpOutput == "":
	print "Error: "+ cpError
else:
        print "Output: " + cpOutput

# Changing ownership in the home directory to be owned by the user.
chownData = Popen(['chown','-Rv', username + ":" + groupname, dirPath ], stdout = PIPE, stderr=PIPE)
chOutput = chownData.stdout.read()
chError = chownData.stderr.read()

if chOutput == "" :
	print "Error: "+ chError
else:
        print "Output: " + chOutput
print "done!"

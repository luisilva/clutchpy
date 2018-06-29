from subprocess import Popen, PIPE
import sys


def questiona():
    answer = raw_input("Enter the user directory path your would like to fix "
                       "ownership on (/n/<pi_lab>/Users): ")
    answer = answer.strip()
    return answer


def questionb():
    answer = raw_input("I'm going to attempt to chown these directorires. \n "
                       "Please make sure all users have uid's in AD. \n "
                       "Proceed with chowning? (y/n): ")
    if answer.lower().strip() == "y" or answer.lower().strip() == "yes":
        return 1
    else:
        return 0


homeDirPath = questiona()

dirlist = Popen(['ls', homeDirPath], stdout=PIPE, stderr=PIPE)
lsOutput = dirlist.stdout.read()
lsError = dirlist.stderr.read()

if lsOutput == "" and lsError == "":
    print "no directories here!"
elif lsOutput != "":
    print "Directories to be chowned: \n" + lsOutput
else:
    print "Error: " + lsError

answerb = questionb()

errors = []

if answerb == 1:
    for n in lsOutput.splitlines():
        n = n.lower()
        print "chowning %s/%s to %s" % (homeDirPath, n, n)
        chowner = Popen(['chown', '-Rv', n, homeDirPath + '/' + n],
                        stdout=PIPE, stderr=PIPE)
        chOutput = chowner.stdout.read()
        chError = chowner.stderr.read()
        if chOutput == "" and chError == "":
            print "nothing happen!?"
        elif chOutput != "":
            print "Output: " + chOutput
        else:
            print "Error: " + chError
            errors.append(n)
else:
    sys.exit()

if len(errors) == 0:
    print "That went great. Nice job!"
else:
    print ("Um so there were some errors, you may what to look"
           " into these directories: \n")
    for things in errors:
        print things

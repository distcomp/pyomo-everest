import sys
import os
import everest
import time
import argparse
import pe_config

UPDATE_PERIOD_IN_SEC = 7*24*3600 - 5*3600

def createParser ():
	parser = argparse.ArgumentParser(description='Get/update everest token. If [TOKEN] doesn\'t exist it will be created')
	parser.add_argument('-t', '--token', default='.token', nargs='?',
                            required=False, help='Token file name, <.token> by default')
	return parser
# Add testDir arg to store results !!!

def getDD_MM_YY_HH_MM():
        return time.strftime("%d-%m-%Y-%H:%M", time.gmtime())

parser = createParser()
args = parser.parse_args()

tokenName = args.token

tokenGotTime = 0
if os.path.isfile(tokenName):
	tokenGotTime = os.stat(tokenName).st_ctime

if tokenGotTime + UPDATE_PERIOD_IN_SEC >= time.time():
	print "Token <" + tokenName + "> is still valid"
        sys.exit(0)

token = everest.get_token('https://everest.distcomp.org',
                          pe_config.EVEREST_LOGIN,
                          pe_config.EVEREST_PASSW,
                          'PE_' + getDD_MM_YY_HH_MM())
with open(tokenName,'w') as f:
        f.write(token)
print "Token <" + tokenName + "> has been updated"

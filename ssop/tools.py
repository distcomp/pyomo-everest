import os
import datetime
import time
import platform

import argparse


import ssop_config
import everest

def getDD_MM_YY_HH_MM():
    return time.strftime("%d-%m-%Y-%H:%M", time.gmtime())

def get_token(path):
    print 'Try to get token[' + ssop_config.SSOP_TOKEN_FILE + ']'
    manualLogin = False
    if not isinstance(ssop_config.EVEREST_LOGIN, str):
        manualLogin = True
    elif len(ssop_config.EVEREST_LOGIN) == 0:
        manualLogin = True

    if not isinstance(ssop_config.EVEREST_PASSW, str):
        manualLogin = True
    elif len(ssop_config.EVEREST_PASSW) == 0:
        manualLogin = True

    if not manualLogin:
        token = everest.get_token('https://everest.distcomp.org',
                          ssop_config.EVEREST_LOGIN,
                          ssop_config.EVEREST_PASSW,
                          'ssop_' + getDD_MM_YY_HH_MM())
    else:
        import getpass
        login = raw_input('Your Everest login: ')
        pw = getpass.getpass('Your Everest password: ')
        token = everest.get_token('https://everest.distcomp.org',
                          login,
                          pw,
                          'ssop_' + getDD_MM_YY_HH_MM())


    with open(path, 'w') as f:
        f.write(token)
    print "Token[" + path + "] has been updated"

    return

def makeSession(name, tokenPath):
    with open(tokenPath, 'r') as f:
        token = f.read().strip()
    try:
        session = everest.Session(name, 'https://everest.distcomp.org', token=token)
        return session
        # # session.__checkJobs()
        # session.close()
        # return True
    except Exception as err:
        print('Error while creating session[' + name + ']:', err)
        return None

def check_token(path, resourceId, application='sol/hostname'):
# Test token by call simple application
    print 'Checking token=[' + path + ']'
    with open(path, 'r') as f:
        token = f.read().strip()
    try:
        session = everest.Session('CheckToken', 'https://everest.distcomp.org', token=token)
        app = everest.App(application, session)
        job = app.run({}, [resourceId])
        print(job.result())  # blocks until job is completed!
        session.close()
        return True
    except Exception as err:
        print("Error while checking token:", err)
        return False

def check_token_time(path, timeInterval):
    print 'Checking token=[' + path + ']'
    try:
        tokentime = os.path.getmtime(path)
    except OSError:
        return False
    print 'Token mtime: ' + str(tokentime)
    print 'Token mdata: ' + str(datetime.datetime.utcfromtimestamp(tokentime))
    if tokentime + timeInterval >= time.time():
        return True
    else:
        return False

def update_token(path):
    print 'token=[' + path + ']'
    # if not check_token_time(path, ssop_config.UPDATE_TOKEN_PERIOD_IN_SEC):
    if not check_token(path, ssop_config.SSOP_RESOURCES['vvvolhome'], 'sol/hostname'):
            get_token(path)
    return

def makeSSOPtmpDir(sess): # Create temporary folder for stubs & sols
    path2tmpDir = ssop_config.SSOP_DEFAULT_WORKING_DIR + '/' + sess.name
    return path2tmpDir

def makeParser():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-do', '--do', type=str, default='check_token_time', choices=['get_token', 'check_token_time', 'check_token', 'update_token'],
                        help='The action to be done')
    # parser.add_argument('-inx', '--initx', type=float, nargs='+', default=[], #action='append',
    #                     help='Initial x')
    # parser.add_argument('-inx2', '--initx2', type=float, nargs='+', default=[], #action='append',
    #                     help='Initial x21, x22')

    return parser



if __name__ == "__main__":
    parser = makeParser()
    args = parser.parse_args()
    # print(args)
    vargs = vars(args)
    print(vargs)
    action = vargs['do']
    if action == 'get_token':
        get_token(ssop_config.SSOP_TOKEN_FILE)
    if action == 'check_token':
        check_token(ssop_config.SSOP_TOKEN_FILE, ssop_config.SSOP_RESOURCES['vvvolhome'], 'sol/hostname')
    if action == 'check_token_time':
        if check_token_time(ssop_config.SSOP_TOKEN_FILE, ssop_config.UPDATE_TOKEN_PERIOD_IN_SEC): #(ssop_config.SSOP_TOKEN_FILE, ssop_config.SSOP_RESOURCES['vvvolhome'], 'sol/hostname')
            print "Token seems to be VALID"
        else:
            print "Token seems to be INVALID"
    if action == 'update_token':
        update_token(ssop_config.SSOP_TOKEN_FILE)

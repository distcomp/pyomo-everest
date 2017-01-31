import everest
import argparse
import os
import time

# COMMAND OPTIONS *******************************************************************************************

parser = argparse.ArgumentParser(description='Run Python API examples')
parser.add_argument('--debug', help='debug HTTP requests and responses', action="store_true")
args = parser.parse_args()

if args.debug:
    import logging
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.getLogger().setLevel(logging.DEBUG)

    # these two lines enable debugging at httplib level (requests->urllib3->httplib)
    # you will see the REQUEST, including HEADERS and DATA, and RESPONSE with HEADERS but without DATA.
    # the only thing missing will be the response.body which is not logged.
    import httplib
    httplib.HTTPConnection.debuglevel = 1

    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True


# INTERESTING STUFF BEGINS HERE *****************************************************************************

# # create session with username and password
# import getpass
# pswd = getpass.getpass('Password: ')
# session = everest.Session(
#     'Python API Test',
#     'https://everest.distcomp.org',
#     user = 'sol',
#     password = pswd
# )

# create session by using existing token
with open('.token') as f:
    token = f.read().strip()
session = everest.Session(
    'Python API Test',
    'https://everest.distcomp.org',
    token = token
)

# define some apps (via app IDs)
hostname = everest.App('52b1d2d13b0000a00071977d', session)
sleep = everest.App('52b1ce8f3d00007a007a7189', session)
append = everest.App('52b1d2013b00008800719779', session)

# define some resources (via resource IDs)
test = '53ad28ca35000042009832de'

# run tests
try:

    print("--- TEST HOSTNAME ---")
    job = hostname.run({}, [test])
    print(job.result()) # blocks until job is completed!

    print("--- TEST SLEEP ---")
    job = sleep.run({'duration': 10}, [test]) # pass inputs dict and resources list
    print(job.result())

    print("--- TEST SLEEP SERVICE (WITH CANCEL) ---")
    job = sleep.run({'duration': 60}, [test])
    time.sleep(10)
    job.cancel() # job is not cancelled immediately (only after acknowledgement from an agent)
    try:
        print(job.result())
    except everest.JobException as e: # job is cancelled!
        print(e)

    print("--- TEST APPEND (TWO CHAINED JOBS) ---")
    #
    # job1 -> job2
    #
    with open('test.txt', 'w') as f:
        f.write('some data...')
    job1 = append.run(
        {
            'message': 'hello everest!',
            'file': open('test.txt', 'rb') # input file should be passed as a file object
        },
        [test]
    )
    job2 = append.run(
        {
            'message': 'goodbye everest!',
            'file': job1.output('file') # pass job output to another job (non-blocking)
        },
        [test]
    )
    result = job2.result()
    session.getFile(result['file'], 'test2.txt') # download output file
    with open('test2.txt') as f:
        print(f.read())
    os.remove('test.txt')
    os.remove('test2.txt')

    print("--- TEST DIAMOND-SHAPED WORKFLOW ---")
    #   A
    #  / \
    # B   C
    #  \ /
    #   D
    jobA = hostname.run({}, [test])
    jobB = hostname.run({'a': jobA.output('hostname')}, [test]) # dummy input 'a' is added to simulate dependency
    jobC = hostname.run({'a': jobA.output('hostname')}, [test])
    jobD = hostname.run({'b': jobB.output('hostname'), 'c': jobC.output('hostname')}, [test])
    print(jobD.result())

    print("--- TEST DIAMOND-SHAPED WORKFLOW (BROKEN) ---")
    #   A (FAILED)
    #  / \
    # B   C
    #  \ /
    #   D (BROKEN)
    jobA = sleep.run({'duration': -10}, [test]) # this job will fail (negative duration), and other ones will be broken
    jobB = hostname.run({'a': jobA.output('hostname')}, [test])
    jobC = hostname.run({'a': jobA.output('hostname')}, [test])
    jobD = hostname.run({'b': jobB.output('hostname'), 'c': jobC.output('hostname')}, [test])
    try:
        print(jobD.result())
    except everest.JobException as e: # job is broken!
        print(e)

    print("--- TEST BAG OF TASKS ---")
    tasks = []
    for n in range(1,11):
        tasks.append(
            {'duration': n*3}
        )
    jobs = sleep.runAll(tasks, [test])
    for job in jobs:
        result = job.result()
        if result == {}:
            print('sleep(%d) -> DONE' % (job.inputs['duration']))

    print("--- TEST GET JOBS AND JOB DELETE ---")
    jobs = session.getJobs() # get all user jobs
    for job in jobs:
        print(job)
        # delete jobs for specific apps
        if job.app_id == hostname.id or job.app_id == sleep.id or job.app_id == append.id:
            job.delete()

finally:
    # always close the session on exit
    session.close()
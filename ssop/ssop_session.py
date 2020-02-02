import os
import sys
import argparse
from zipfile import ZipFile, ZIP_DEFLATED
import shutil
import tempfile
from collections import defaultdict, OrderedDict
import json
import calendar
import time
import string
import re

import requests
import everest

import ssop_config

def makeParser():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-pr', '--problem', default="problem", help='problem name')
    parser.add_argument('-wd', '--workdir', default=ssop_config.SSOP_DEFAULT_WORKING_DIR,
                        help='working dir to store *.opt, *.nl and *.sol files')
    parser.add_argument('-t', '--token', default=ssop_config.SSOP_TOKEN_FILE,
                        help='token obtainable with everest.py')
    parser.add_argument('-r', '--resources', nargs='+', default=[],
                        help='everest resources to be used') # ssop_config.SSOP_RESOURCES.values()
    parser.add_argument('-s', '--solver', default='ipopt', choices=['ipopt', 'scip', 'fscip', 'none'],
                        help='solver to use')
    parser.add_argument('-p', '--parameters', default=[], nargs='+',
                        help='solver parameters as k=v pairs')
    parser.add_argument('-pf', '--parameters-file', action='append', default=[],
                        help='files with solver parameters. Overrides -p params')
    # parser.add_argument('-l', '--get-log', action='store_true',
    #                     help='download job log')
    # parser.add_argument('-ss', '--save-status', action='store_true',
    #                     help='save solution status and objective value')
    # parser.add_argument('-sm', '--stop-mode', type=int, default='0',
    #                     help='0 - run until all tasks finish, 1 - run until any task finish, return best solution as result')
    # parser.add_argument('-ii', '--initial-incumbent', type=float, default='1e23',
    #                     help='start task with initial incumbent')
    parser.add_argument('-nlf', '--nlinfile', type=argparse.FileType('rb'),
                        help='file with a list of input NL-files')
    parser.add_argument('-o', '--out-prefix', default='out', help='output prefix')
    parser.add_argument('-ur', '--use-results', help='Skip parameter sweep run by using already computed results')
    parser.add_argument('nls', nargs='*', default=[], help='input NL-files')
    parser.add_argument('-db', '--debug', action='store_true')
    return parser

class SsopSession:
    def __init__(self, name='problem', token=ssop_config.SSOP_TOKEN_FILE, appId=ssop_config.SSOP_ID, resources=[], \
                 workdir=ssop_config.SSOP_DEFAULT_WORKING_DIR, debug=False):
        self.name = name
        with open(token) as f:
            self.token = f.read().strip()
        self.session = everest.Session('ssop-' + name, 'https://optmod.distcomp.org', token=self.token)
        # self.ssop = everest.App(ssop_config.SSOP_ID, self.session)
        self.ssopApp = everest.App(appId, self.session)
        self.workdir = workdir
        self.resources = resources
        self.nJobs = 0
        self.nProblems = 0
        self.debug = debug


    def makeFileName(self, fname, suffix=""):
        return os.path.join(self.workdir, fname + suffix)

    def saveResults(selfself, resZipName, nlNames):
        return

    def runJob(self, nlNames, optFile, solver="ipopt"):
        """
        Run job with the list of NL-files
        :param nlNmes: list of NL-files without .nl extension, should be placed in the workdir
        :param optFile: file with solver options, should be placed in the workdir
        :param solver: {ipopt|scip|...}
        :return: number of SOL-files placed in workdir
        """
        nlFIles2str = "".join(nlNames[i]+" " for i in range(len(nlNames)))

        with open(self.makeFileName(self.name, '.plan'), 'wb') as f:
            f.write('parameter nlname %s\n' % (nlFIles2str))
            f.write('parameter options %s \n' % (optFile))
            f.write('parameter solver %s \n' % (solver))
            f.write('input_files ${nlname}.nl ${options}\n')
            f.write('command run-%s.sh ${nlname} ${options}\n' % (solver))
            f.write('output_files ${nlname}.sol ${nlname}.log.txt stderr\n')
            f.close()

        with ZipFile(self.makeFileName(self.name, '.zip'), 'w', ZIP_DEFLATED) as z:
            for f in nlNames:
                z.write(self.makeFileName(f,".nl"), arcname=f + ".nl")
            z.write(self.makeFileName(optFile), arcname=optFile)
            z.close()

        jobName = self.name + "-" + str(self.nJobs+1)
        jobId = ""
        if self.debug:
            print("plan: %s" % (self.makeFileName(self.name, '.plan')))
            print("files: %s" % (self.makeFileName(self.name, '.zip')))
        try:
            # ssop = everest.App(ssop_config.SSOP_ID, self.session)
            job = self.ssopApp.run({
                "plan": open(self.makeFileName(self.name, '.plan'), 'rb'),
                "files": open(self.makeFileName(self.name, '.zip'), 'rb')
            }, resources=self.resources, job_name=jobName)
            jobId = job.id
            # print("JobId" + jobId)
        except Exception as e:
            print("Job[" + jobName + "] caused:" + e.message)
            self.session.close()
            return
        self.nJobs = self.nJobs + 1
        print("Job" + jobName + ", " + jobId + " is running")

        try:
            result = job.result()
        except everest.JobException:
            result = self.session.getJobStatus(job.id)
            if 'result' in result:
                print 'Job failed, result downloaded'
                self.session.getFile(result['result']['results'], self.makeFileName(jobName + '-results.zip'))
                self.saveResults(self.makeFileName(jobName + '-results.zip'), nlNames)
                if self.debug:
                    print "Downloading job's log..."
                    self.session.getJobLog(job.id, jobName + '.log')
            else:
                print 'Job failed, no result available'
            sys.exit(1)
        except KeyboardInterrupt:
            print 'Cancelling the job...'
            try:
                job.cancel()
            except requests.exceptions.HTTPError as e:
                sys.stderr.write('Response from the server: %s\n' % e.response.content)
                sys.stderr.write('Headers of the request: %s\n' % e.request.headers)
                raise
            try:
                result = job.result()
            except everest.JobException as e:
                print e
            return

        self.session.getFile(result['results'], self.makeFileName(jobName + '-results.zip'))
        self.saveResults(self.makeFileName(jobName + '-results.zip'), nlNames)
        # tasksRes = saveResults(makeName('-results.zip'), stubNames, args)
        if self.debug:
            print "Downloading job's log..."
            self.session.getJobLog(job.id, args.out_prefix + '.log')
            # parseJobLog(args.out_prefix + '.log', tasksRes, args)

        return

if __name__ == "__main__":
    parser = makeParser()
    args = parser.parse_args()
    # print(args)
    vargs = vars(args)
    for arg in vars(args):
        print arg, getattr(args, arg)

    theSession = SsopSession(name=args.problem, resources=[ssop_config.SSOP_RESOURCES["vvvolhome"]], debug=args.debug)

    theSession.runJob(["tmpabc0007_00000", "tmpabc0007_00001", "tmpabc0007_00002", "tmpabc0007_00003"], "peipopt.opt")

    theSession.session.close()

    print("Done")


from __future__ import print_function
from future.utils import iteritems

import os
import sys
import argparse

# import pyomo.environ as pyo
#
# from pyomo.core.base.PyomoModel import *
# from pyomo.core.base.param import *
# from pyomo.core.base.var import *
# from pyomo.core.base.sets import *
# from pyomo.core.base.rangeset import *
# from pyomo.core.base.objective import *
# from pyomo.core.base.constraint import *
# from pyomo.core.base.set_types import *
#
# from pyomo.opt import *
from write import write_nl_only
from write import get_smap_var
from read import read_sol_smap_var

# import ssop_config
from ssop_session import *

import ssop_config
from testModel import TestProblem

def binaryHypercube(N, UpN = 15, type="01"):
    if N > UpN:
        raise ValueError('N(' + str(N) + ') > up limit (' + str(UpN) + ')')
    if not type in ["01", "-11"]:
        raise ValueError('Unknown type = ' + type + ' Not in ["01", "-11"]')

    print('Hypercube N = ', N)
    s = '{:0' + str(N) + 'b}'
    res = []
    for n in range(0, 2 ** N):
        temp = s.format(n)  # get boolean representation of n
        # print(temp)
        temp = list(temp)  # boolean -> to list of boolean digits '0'|'1'
        # tempList = [int((int(c))) for c in temp]  # 0 -> -1; 1 -> 1
        res.append(temp)
    if type == "01":
        for k in range(len(res)):
            res[k] = [int(b) for b in res[k]]
    else:
        for k in range(len(res)):
            res[k] = [(2*int(b) - 1) for b in res[k]]

    return res

def makeParser():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-pr', '--problem', default="maxVofCube", help='problem name')
    parser.add_argument('-wd', '--workdir', default='/mnt/hgst2/ext4/git_work/pyomo-everest/ssop/.tmp', help='working directory')
    parser.add_argument('-s', '--solver', default='ipopt', choices=['ipopt', 'scip'], help='solver to use')
    parser.add_argument('-n', '--nofjobs', default=2, choices=[2,3,4], type=int, help='Number of SSOP Jobs in main test')
    parser.add_argument('-cf', '--cleanfiles', action='store_true', help='clean working directory')
    parser.add_argument('-cj', '--cleanjobs', action='store_true', help='clean jobs from server')
    parser.add_argument('-x', '--extra', action='store_true', help='extra tests')
    return parser

def makeIpoptOptionsFile(workdir, optFileName):
    # see https://coin-or.github.io/Ipopt/OPTIONS.html
    with open(workdir + "/" + optFileName, 'w') as f:
        f.write("linear_solver ma57\n")
        f.write("max_iter 10000\n")
        f.write("constr_viol_tol 0.0001\n")
        f.write("warm_start_init_point yes\n")
        f.write("warm_start_bound_push 1e-06\n")
        f.write("print_level 4\n")
        f.write("print_user_options yes\n")
        f.close()
    return

def makeScipOptionsFile(workdir, optFileName):
    # https://scip.zib.de/doc-6.0.2/html/PARAMETERS.php
    with open(workdir + "/" + optFileName, 'w') as f:
        f.write('display/freq = 100\n')
        f.write('display/verblevel = 4\n')
        f.write('limits/gap = 1e-06\n')
        f.write('limits/memory = 28000\n')
        f.close()
    return

def makeNlFiles(workdir, **params):
    problem = params["problem"]
    bCube = params["bCube"]
    shiftDelta = params["shiftDelta"]

    nlNames = []
    dictModels = {}

    for b in bCube:
        s = ""
        for bd in b:
            s = "%s%d" % (s, bd)
        probName = problem + '_' + s
        print("Make NL for ", probName)

        initx=[]
        for bb in b:
            initx.append(0)

        theModel = TestProblem(name=probName, initx=initx, dim=len(b), shiftSigns=b, shiftDelta=shiftDelta)

        dictModels[probName] = theModel
        nlName = write_nl_only(theModel.model, workdir + '/' + probName,  symbolic_solver_labels=True)
        nlNames.append(probName)

    return nlNames, dictModels

def checkResults(workdir, solvedNlNames, dictModels):
    for nlname in solvedNlNames:
        theModel = dictModels[nlname]
        # the trick with fast reading: smap is generated for read only!
        smap = get_smap_var(theModel.model)
        results = read_sol_smap_var(theModel.model, workdir + "/" + nlname, smap)
        theModel.model.solutions.load_from(results)
        # solution have been loaded to the model
        print("Solutions for ", nlname.split("_")[-1])
        valBuf = ""
        idxBuf = ""
        for idx in theModel.model.idx:
            valBuf = valBuf + ("%5.2f " % theModel.model.x[idx]())
            idxBuf = idxBuf + ("x%d " % idx)

        print("[%s] = [%s]" % (idxBuf, valBuf))

    return

if __name__ == "__main__":
    parser = makeParser()
    args = parser.parse_args()
    # vargs = vars(args)
    print('Arguments of the test')
    print('======================')
    for arg in vars(args):
        print(arg + ":", getattr(args, arg))
    print('======================')

    workdir = args.workdir
    solver = args.solver

    bCube = binaryHypercube(3, type="-11")
    resources_list = [ssop_config.SSOP_RESOURCES["shark1vvv"]] # test-pool-scip-ipopt['']] #["vvvolhome2"]] # ["ui4.kiae.vvvol"]] 'hse'
    theSession = SsopSession(name=args.problem, resources=resources_list, \
                             workdir=workdir, debug=False)
    # theSession = SsopSession(name=args.problem, resources=[ssop_config.SSOP_RESOURCES["ui4.kiae.vvvol"]], \
    #                          workdir=workdir, debug=False)

    # Variables declarations for Python 3.*
    optFile = ""
    solved = []
    unsolved = []
    jobId = ""

    # Write NL-files
    shiftDelta = 0.15
    print("shiftDelta=%4.2f" % (shiftDelta))
    nlNames, dictModels = makeNlFiles(workdir, problem=args.problem, bCube=bCube, shiftDelta=shiftDelta)

    # Write options file
    if solver == "scip":
        optFile = 'scipdemo.set'
        # makeScipOptionsFile(workdir, optFile)
        makeSolverOptionsFile(workdir + "/" + optFile, solver="scip",  \
                        dictOptVal={"display/freq":100, "display/verblevel": 4, \
                                    "limits/gap":1e-06, "limits/memory": 28000}
                                         )
    if solver == "ipopt":
        optFile = 'ipopt.opt'
        # makeIpoptOptionsFile(workdir, optFile)
        makeSolverOptionsFile(workdir + "/" + optFile, solver="ipopt",  \
                                         linear_solver="ma57", max_iter=10000, \
                                         constr_viol_tol=0.0001,
                                         warm_start_init_point="yes", warm_start_bound_push=1e-06, \
                                         print_level=4, print_user_options="yes")

    # Solve all problems by SSOP
    if solver == "ipopt":
        solved, unsolved, jobId = theSession.runJob(nlNames, optFile) # by default solver = "ipopt"
    if solver == "scip":
        solved, unsolved, jobId = theSession.runJob(nlNames, optFile, solver="scip")

    print("solved:   ", solved)
    print("unsolved: ", unsolved)
    print("Job %s is finished" % jobId)

    # Check results
    checkResults(workdir, solved, dictModels)

    # ===============================================================
    # || Change the set of models: increase shift of cube vertices ||
    # ===============================================================
    for k in range(1, args.nofjobs):
        print("===============================================================")
        print("|| Change the set of models: increase shift of cube vertices ||")
        print("===============================================================")
        # print("========== Next set of problems ... ==========")
        shiftDelta = shiftDelta + 0.05
        print("The shiftDelta = %4.2f" % (shiftDelta))
        nlNames, dictModels = makeNlFiles(workdir, problem=args.problem, bCube=bCube, shiftDelta=shiftDelta)

        # Solve all problems by the SAME SESSION !

        if solver == "ipopt":
            solved, unsolved, jobId = theSession.runJob(nlNames, optFile) # by default solver = "ipopt"
        if solver == "scip":
            solved, unsolved, jobId = theSession.runJob(nlNames, optFile, solver="scip")

        print("solved:   ", solved)
        print("unsolved: ", unsolved)
        print("Job %s is finished" % (jobId))

        # Check results
        checkResults(workdir, solved, dictModels)

    # Call different solvers as extra tests
    if args.extra:
        print('=====================================\nTry successive calls: SCIP and IPOPT')
        shiftDelta = 0.3
        print("The shiftDelta = %4.2f" % (shiftDelta))
        nlNames, dictModels = makeNlFiles(workdir, problem=args.problem, bCube=bCube, shiftDelta=shiftDelta)

        # !!! If you change solver DO NOT FORGET to select another options file !!!
        optFile = 'scipdemo.set'
        makeScipOptionsFile(workdir, optFile)
        solved, unsolved, jobId = theSession.runJob(nlNames, optFile, solver="scip")
        checkResults(workdir, solved, dictModels)

        optFile = 'ipopt.opt'
        makeIpoptOptionsFile(workdir, optFile)
        solved, unsolved, jobId = theSession.runJob(nlNames, optFile, solver="ipopt")
        checkResults(workdir, solved, dictModels)

    # Clean working directory to free disk space at local host, MAY BE
    if args.cleanfiles:
        theSession.deleteWorkFiles([".nl", ".row", ".col", ".sol", ".zip", ".plan"])

    # Delete jobs created to save disk space at Everest server , MAY BE
    if args.cleanjobs:
        theSession.deleteAllJobsExceptLast(2)

    # CLOSE THE SESSION !!! MUST BE
    theSession.session.close()

    print("Done")

import os
import sys
import argparse

import pyomo.environ as pyo

from pyomo.core.base.PyomoModel import *
from pyomo.core.base.param import *
from pyomo.core.base.var import *
from pyomo.core.base.sets import *
from pyomo.core.base.rangeset import *
from pyomo.core.base.objective import *
from pyomo.core.base.constraint import *
from pyomo.core.base.set_types import *

from pyomo.opt import *
from write import write_nl_only
from write import get_smap_var

from read import read_sol_smap_var

import ssop_config
from ssop_session import *

import ssop_config
from testModel import TestProblem

def binaryHypercube(N, UpN = 15, type="01"):
    if N > UpN:
        raise ValueError('N(' + str(N) + ') > up limit (' + str(UpN) + ')')
    if not type in ["01", "-11"]:
        raise ValueError('Unknown type = ' + type + ' Not in ["01", "-11"]')

    print 'Hypercube N = ', N
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
    parser.add_argument('-wd', '--workdir', default='/home/vladimirv/python_work/pyomo-everest/ssop/.demo', help='working directory')
    return parser

if __name__ == "__main__":
    parser = makeParser()
    args = parser.parse_args()
    # vargs = vars(args)
    for arg in vars(args):
        print arg, getattr(args, arg)

    workdir = args.workdir

    bCube = binaryHypercube(3, type="-11")
    nlNames = []
    dictModels = {}
    for b in bCube:
        s = "%d%d%d" % (b[0],b[1],b[2])
        probName = args.problem + '_' + s
        print("Make NL for ", probName)

        theModel = TestProblem(name=probName, shiftSigns=b)

        dictModels[probName] = theModel
        nlName = write_nl_only(theModel.model, workdir + '/' + probName,  symbolic_solver_labels=False)
        nlNames.append(probName)

    # Write options file
    optFile = 'ipopt.opt'
    with open(workdir + "/" + optFile, 'wb') as f:
        f.write('linear_solver ma57\n')
        f.write('max_iter 10000\n'     )
        f.write('constr_viol_tol 0.0001\n')
        f.write('warm_start_init_point yes\n')
        f.write('warm_start_bound_push 1e-06\n')
        f.write('print_level 4\n')
        f.write('print_user_options yes\n')
        f.close()

    # Solve all problems
    theSession = SsopSession(name=args.problem, resources=[ssop_config.SSOP_RESOURCES["vvvolhome"], ssop_config.SSOP_RESOURCES["vvvoldell"]], \
                             workdir=workdir, debug=False)
    solved, unsolved, jobId = theSession.runJob(nlNames, "ipopt.opt")
    print("solved:   ", solved)
    print("unsolved: ", unsolved)
    print("Job %s is finished" % (jobId))

    # Check results
    for nlname in solved:
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

    # ===============================================================
    # || Change the set of models: increase shift of cube vertices ||
    # ===============================================================
    print("===============================================================")
    print("|| Change the set of models: increase shift of cube vertices ||")
    print("===============================================================")
    # print("========== Next set of problems ... ==========")
    shiftDelta = 0.2
    print("The shiftDelta = %f" % (shiftDelta))
    nlNames = []
    dictModels = {}
    for b in bCube:
        s = "%d%d%d" % (b[0],b[1],b[2])
        probName = args.problem + '_' + s
        print("Make NL for ", probName)

        theModel = TestProblem(name=probName, shiftSigns=b, shiftDelta=shiftDelta)

        dictModels[probName] = theModel
        nlName = write_nl_only(theModel.model, workdir + '/' + probName,  symbolic_solver_labels=False)
        nlNames.append(probName)

    # Solve all problems by the SAME SESSION !

    solved, unsolved, jobId = theSession.runJob(nlNames, "ipopt.opt")
    print("solved:   ", solved)
    print("unsolved: ", unsolved)
    print("Job %s is finished" % (jobId))

    # Check results
    for nlname in solved:
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

    # CLOSE THE SESSION !!!
    theSession.deleteAllJobs()
    theSession.session.close()

    print("Done")








import pyomo.dae.simulator
import pyomo.environ as pyo
from pyomo.opt import SolverFactory, TerminationCondition
from write import write_nl_only, get_smap_var
from read import read_sol_smap_var
import sys
# import casadi as cs

import subprocess

import argparse

def test_casadi_model():
    model = pyo.ConcreteModel()
    model.x = pyo.Var(initialize=1.)
    model.y = pyo.Var(initialize=5.)
    model.o = pyo.Objective(expr=((pyo.sin(model.x) - 2*model.y)**2 + 10*model.y))
    model.cxLo = pyo.Constraint(expr=model.x >= 1)
    model.cxUp = pyo.Constraint(expr=model.x <= 5)
    model.cyLo = pyo.Constraint(expr=model.y >= 1)
    model.cyUp = pyo.Constraint(expr=model.y <= 5)
    cs_cyUp = pyomo.dae.simulator.convert_pyomo2casadi(model.cyUp)
    cs_model = pyomo.dae.simulator.convert_pyomo2casadi(model)
    # model.x.set_value(1.0)
    return (cs_cyUp, cs_model)

def create_model():
    m = pyo.ConcreteModel()
    m.x = pyo.Var(initialize=1., bounds=(1, 5))
    m.y = pyo.Var(initialize=5., bounds=(2, 6))
    m.o = pyo.Objective(expr=((pyo.sin(m.x) - 2*m.y)**2 + 10*m.y))
    m.SomeConstr = pyo.Constraint(expr= m.x**2 + m.y**2 <= 27)
    # model.cxUp = pyo.Constraint(expr=model.x <= 5)
    # model.cyLo = pyo.Constraint(expr=model.y >= 1)
    # model.cyUp = pyo.Constraint(expr=model.y <= 5)
    # model.x.set_value(1.0)
    return m

def check_sol(model):
    print("Objective: %s" % (model.o()))
    print("x: %s" % (pyo.value(model.x)))
    print("y: %s" % (pyo.value(model.y)))
    print("x+log(y): %s" % (pyo.value(model.x + pyo.log(model.y))))
    print("x+y by quicksum: %s" % (pyo.value(pyo.quicksum(v for v in (model.x, model.y)))))


def makeParser():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-s', '--solver', default='ipopt', choices=['ipopt', 'scip'], help='solver to use')
    parser.add_argument('-f', '--fast', action='store_true', help='Fast mode: model->nl->solver->readSOL->model')
    parser.add_argument('-w', '--writenl', action='store_true', help='Write NL-file & SOLVE')
    parser.add_argument('-r', '--readsol', action='store_true', help='Read SOL-file into model')
    return parser

if __name__ == "__main__":
    print("Python", sys.version)
    print("Pyomo", pyomo.__version__)
    # test_casadi_model()
    # quit()
    model = create_model()
    # write_nl_smap(model, "/mnt/hgst2/ext4/vc_work/testProject/ex.nl")
    # write_nl_only(model, "/mnt/hgst2/ext4/vc_work/testProject/ex_only_nl.nl")
    print('======== The model (the problem) in symbolic form ========')
    model.pprint()
    print('||||||||||||||||||||||||||||||||||||||||||||||||||||||||||\n')

    parser = makeParser()
    args = parser.parse_args()
    IPOPT_EXE = '/opt/scipopt921/bin/ipopt'
    SCIP_EXE = '/opt/scipopt921/bin/scip'
    if args.fast :
        # All model-writeNL-file->solver->readSOL-file->model pipeline is hidden
        if args.solver == 'ipopt':
            print('======================= Try IPOPT =======================')
            with SolverFactory(IPOPT_EXE) as opt:   #/opt/scipopt921/bin/ipopt /opt/solvers/bin/ipopt
                # model.pprint()
                print("Before SOLVE x+y: %s" % (pyo.value(model.y + model.x)))
                # opt.options["print_level"] = 4
                opt.options['print_user_options'] = 'yes'
                opt.options['option_file_name'] = 'ipopt.opt'

                results = opt.solve(model, load_solutions=True, tee=True)

                if results.solver.termination_condition != TerminationCondition.optimal:
                    raise RuntimeError('Solver did not report optimality:\n%s'
                                       % (results.solver))
                # model.solutions.load_from(results)
                check_sol(model)
                print('|||||||||||||||||||||||| IPOPT |||||||||||||||||||||||||||\n')

        if args.solver == 'scip':
            print('======================= Try SCIP =======================')
            with SolverFactory(SCIP_EXE) as opt:   #/opt/scipopt921/bin/ipopt /opt/solvers/bin/ipopt
                # model.pprint()
                print("Before SOLVE x+y: %s" % (pyo.value(model.y + model.x)))
                # opt.options["print_level"] = 4
                # By default scip.set in the current folder will be used

                results = opt.solve(model, load_solutions=True, tee=True)

                if results.solver.termination_condition != TerminationCondition.optimal:
                    raise RuntimeError('Solver did not report optimality:\n%s'
                                       % (results.solver))
                # model.solutions.load_from(results)
                check_sol(model)
            print('||||||||||||||||||||||||  SCIP ||||||||||||||||||||||||||\n')

        quit()

    if args.writenl:
        # Write NL-file
        NL_NAME = 'ex'
        print(f'======== Write NL-file as {NL_NAME}.nl ========')
        write_nl_only(model, NL_NAME, symbolic_solver_labels=True)
        print(f'======== DONE ========\n')

        if args.solver == 'ipopt':
            print('======================= Try IPOPT =======================')
            subprocess.check_call(
                IPOPT_EXE + ' ' + NL_NAME + ".nl" + " -AMPL \"option_file_name=" + "ipopt.opt\" | tee " + NL_NAME + ".ipopt.log.txt",
                shell=True)
            print('|||||||||||||||||||||||| IPOPT |||||||||||||||||||||||||||\n')

        if args.solver == 'scip':
            print('======================= Try SCIP =======================')
            subprocess.check_call(SCIP_EXE + ' ' + NL_NAME + " -AMPL | tee " + NL_NAME + ".scip.log.txt", shell=True)
            print('||||||||||||||||||||||||  SCIP ||||||||||||||||||||||||||\n')

        quit()

    if args.readsol:
        # Read SOL-file
        NL_NAME = 'ex'
        print(f'============ Read SOL-file as {NL_NAME}.sol ============')
        # The trick here is with fast reading: smap is generated for read only!
        smap = get_smap_var(model)
        results = read_sol_smap_var(model, NL_NAME, smap)
        model.solutions.load_from(results)
        check_sol(model)
        print(f'======= Done reading SOL-file as {NL_NAME}.sol ========')

        quit()


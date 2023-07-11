from pyomo.environ import *
from pyomo.opt import SolverFactory, TerminationCondition

def create_model():
    model = ConcreteModel()
    model.x = Var(initialize=1.)
    model.y = Var(initialize=5.)
    model.o = Objective(expr=((model.x - 2*model.y)**2 + 10*model.y))
    model.cxLo = Constraint(expr=model.x >= 1)
    model.cxUp = Constraint(expr=model.x <= 5)
    model.cyLo = Constraint(expr=model.y >= 1)
    model.cyUp = Constraint(expr=model.y <= 5)
    # model.x.set_value(1.0)
    return model

if __name__ == "__main__":

    with SolverFactory("/opt/solvers/bin/ipopt") as opt:
        model = create_model()
        print("Before SOLVE x+y: %s" % (value(model.y + log(model.x))))
        # opt.options["print_level"] = 4
        opt.options['print_user_options'] = 'yes'
        opt.options['option_file_name'] = 'ipopt.opt'
        results = opt.solve(model, load_solutions=True, tee=True)
        if results.solver.termination_condition != TerminationCondition.optimal:
            raise RuntimeError('Solver did not report optimality:\n%s'
                               % (results.solver))
        # model.solutions.load_from(results)
        print("Objective: %s" % (model.o()))
        print("x: %s" % (value(model.x)))
        print("y: %s" % (value(model.y)))
        print("x+log(y): %s" % (value(model.x + log(model.y))))
        print("x+log(y): %s" % (value(quicksum(x for x in (model.x, log(model.y))) )))

# coding=utf-8
import os

import argparse

# from pyomo.environ import *
import pyomo.environ as pyo

# from pyomo.core.base.PyomoModel import *
# from pyomo.core.base.param import *
# from pyomo.core.base.var import *
# from pyomo.core.base.sets import *
# from pyomo.core.base.rangeset import *
# from pyomo.core.base.objective import *
# from pyomo.core.base.constraint import *
# from pyomo.core.base.set_types import *

from pyomo.opt import *
from write import *

from read import read_sol_smap
from read import read_sol_smap_var

class TestProblem:
    def __init__(self, name="testProblem", initx=[0, 0, 0], dim=3, shiftDelta=0.1, shiftSigns=[1, 1, 1], extName='', debug=False, options=None, model_options=''):
        self.name = name
        self.model = pyo.ConcreteModel(name)
        # Dimension of variable space
        self.model.dim = dim
        self.model.idx = pyo.RangeSet(1, dim)

        def init_x(model, i):
            return initx[i-1]
        self.model.x = pyo.Var(self.model.idx, initialize=init_x, within=pyo.Reals, bounds=(-2, 2))

        # Objective as auxiliarry variable. objvar, to be in complience with SCIP
        def init_objvar(model):
            return -sum(init_x(model,i)**2 for i in model.idx)
        self.model.objvar = pyo.Var(initialize=init_objvar, within=pyo.Reals)

        def cons_objvar_rule(model):
            return (-sum(model.x[i]**2 for i in model.idx) <= model.objvar)
        self.model.cons_objvar = pyo.Constraint(rule=cons_objvar_rule)

        def obj_rule(model):
            return model.objvar
        self.model.obj = pyo.Objective(rule=obj_rule, sense=pyo.minimize)
        # =========================================================================

        def ConsUp_rule(model, i):
            if shiftSigns[i-1] > 0:
                exp = (model.x[i] <= 1. + shiftDelta)
            else:
                exp = (model.x[i] <= 1.)
            return exp
        self.model.ConsUp = pyo.Constraint(self.model.idx, rule=ConsUp_rule)

        def ConsLow_rule(model, i):
            if shiftSigns[i-1] < 0:
                exp = (-1 - shiftDelta <= model.x[i])
            else:
                exp = (-1              <= model.x[i])
            return exp
        self.model.ConsLow = pyo.Constraint(self.model.idx, rule=ConsLow_rule)


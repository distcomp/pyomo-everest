# -*- coding: utf-8 -*-
from __future__ import division
from  numpy import *
import subprocess
from pyomo.opt import TerminationCondition
from pyomo.opt import (ReaderFactory,ResultsFormat)
from pyomo.opt import ProblemFormat 

#from  GlobName import *


def PrepStab ( Gr, stab_file, NoR ) :
    _, smap_id = Gr.write( stab_file+".nl", format=ProblemFormat.nl)  # создаем стаб
    symbol_map = Gr.solutions.symbol_map[smap_id]

    nlF = open( stab_file +".nl" )                         # считываем и разбираем структуру
    nls = nlF.read().split("o2\nn1\no5\n")
    nlF.close()
    if len(nls) != NoR+1 :
        print "=========== len =======  ", len(nls), " != NoR + 1"
        quit
    p_1_NoR = nls[0].rfind("n")                             # указатель на 'n'+1/sum_mu1
    nlEND = nls[-1].split("\nn2.0\n")                       # отделяем последний элемент
    if len(nlEND) != 2 :
        print "len(nlEND)", len_nls, "!= 2";
        quit
    nls[-1] = nlEND[0] + "\nn2.0\n"
    return  nls, nlEND, p_1_NoR, symbol_map
#    return  nls, nlEND, p_1_NoR


def makeStab_solve ( stab_file, Gr, nls, nlEND, p_1_NoR, NoR, symbol_map ) :
        nl_mu = open ( stab_file+".nl", "w" )                #  Мастерим стаб для mu=1
        nl_mu.write(nls[0][0:p_1_NoR])                  # до 1/sum_mu1
        sum_mu1 = sum( Gr.mu[s]() for s in Gr.F[0].sR )
        nl_mu.write( "n" + str( 1./sum_mu1 ) + "\no54\n" + str( sum_mu1 ) + "\n")
        for i in range(1,NoR+1) :                     # цикл по интерполяции
          if Gr.mu[i-1] :
#            nl_mu.write("o2\nn1\no5\no54\n4\no0")
            nl_mu.write("o2\nn1\no5\n")
            nl_mu.write(nls[i])
        nl_mu.write(nlEND[1])                           # остатки
        nl_mu.close()

        subprocess.check_call('ipopt -s ' + stab_file+".nl", shell=True)

        with ReaderFactory(ResultsFormat.sol) as reader:
            results = reader( stab_file+".sol" )
        results._smap = symbol_map

        if results.solver.termination_condition != TerminationCondition.optimal:
            raise RuntimeError("Solver did not terminate with status = optimal")
        return results




# -*- coding: utf-8 -*-
from __future__ import division
from  numpy import *
import subprocess
from pyomo.opt import TerminationCondition
from pyomo.opt import (ReaderFactory,ResultsFormat)
from pyomo.opt import ProblemFormat 

import os
import sys
import everest
from zipfile import ZipFile

#==pepepepepepepepepepepe==
import pe_config
import random
#==========================

#from  GlobName import *
# File with options to be sent to IPOPT solver
PEIpoptOptionsFileName = 'peipopt.opt'

# File with Everest session ID
PESessidFile = '__pesessid.txt'
if 'PE_SESSID_FILE' in os.environ.keys(): PESessidFile = os.environ['PE_SESSID_FILE']
PEsessid = '%04d' % (random.randint(0,9999))
f = open(PESessidFile,'w')
f.write(PEsessid)
f.close()

#PE session Id prefix
PEprefix = 'pe'

# File with Everest total number of solved problems PE_N_OF_SOLVED_FILE=pe.out.N_of_solved.txt
PESessNofSolvedFileName = 'pe.' + PEsessid + '.out.N_of_solved.txt'
if 'PE_N_OF_SOLVED_FILE' in os.environ.keys(): PESessNofSolvedFileName = os.environ['PE_N_OF_SOLVED_FILE']

# Disable usr/local/lib/python2.7/dist-packages/requests/packages/urllib3/connectionpool.py:734:
# InsecureRequestWarning: Unverified HTTPS request is being made.
# Adding certificate verification is strongly advised. See: https://urllib3.readthedocs.org/en/latest/security.html InsecureRequestWarning
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
if os.name != 'posix': requests.packages.urllib3.disable_warnings(InsecureRequestWarning) # for Windows, os.name = 'nt'


def writeIpoptOptionsFile(optsDict, fNameOpts = PEIpoptOptionsFileName):
   fOpts = open(fNameOpts,'w')
   for key in optsDict.keys():
      if key != 'solver': fOpts.write('%s %s\n' % (key, str(optsDict[key])))
   fOpts.close()

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
      # nl_mu.write("o2\nn1\no5\no54\n4\no0")
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


def peSolveListOfStubs (listOfStubs, solver='ipopt', opts=PEIpoptOptionsFileName, sessNofSolvedFileName = PESessNofSolvedFileName):
   tokenFile = '.token'
   if 'PE_PATH' in os.environ:
      tokenFile = os.path.join(os.environ['PE_PATH'], '.token')
   
   with open(tokenFile, 'r') as f:
      token = f.read().strip()
   
   # __pesessid.txt - keep pseudo unique ID for the session,
   #                   which must be created somehow before 
   #~ sessIdFile = PESessidFile    
   
   #~ with open(sessIdFile, 'r') as f: 
      #~ sessionId = PEprefix + f.read().strip()
   
   # sessionId looks like "PE####"
   #~ print('token:[' + token + ']' + ' for Session [' + PEprefix + PEsessid + ']')
   session = everest.Session(PEprefix + PEsessid, 'https://everest.distcomp.org', token = token)   
   
   #~ sessNofSolvedFileName = PESessNofSolvedFileName
   N_of_solved = 0
   nl = ''
   
#  read N of solved solved from file
   try:
       f_n_of_solved = open(PESessNofSolvedFileName,'r')
       nl = f_n_of_solved.read().strip()
       N_of_solved = int(nl)
       f_n_of_solved.close()
   except IOError as e:
       print "[%s] I/O error(%s): %s" % (PESessNofSolvedFileName, e.errno, e.strerror)
       raise
   except ValueError:
       print "[%s] Could not convert [%s] to an integer." % (PESessNofSolvedFileName, nl)
   except:
       print "Unexpected error:", sys.exc_info()[0]
       raise
       
   try:
       amplApp = everest.App(pe_config.SOLVE_AMPL_STUB_ID, session)
       problems = []
       for p in listOfStubs:
   		problems.append(
   		   {"optionsString": "",
               "optionsFile": open(PEIpoptOptionsFileName, 'r'),
               "solver": solver,
               "stub": open(p + '.nl', 'r')
              }
           )
       
       jobs = amplApp.runAll(problems,[])
   
       for j in jobs:
           result = j.result()
           arrPath = j.inputs['stub'].split('/')
           pName = (arrPath[len(arrPath) - 1]).split('.')[0]
           print j.id + "[stub]=" + pName
           session.getFile(result['solution'], pName + '.sol')
           session.getFile(result['solve-ampl-stub-log'], pName + '.log')
           N_of_solved = N_of_solved + 1
   except everest.JobException as e:
       print (" runAll caused: " + e)
       raise
   finally:
       session.close()
   
   try:
       f_n_of_solved = open(PESessNofSolvedFileName,'w')
       f_n_of_solved.write(str(N_of_solved))
       f_n_of_solved.close()
   except IOError as e:
       print "I/O error(%s): %s" % (e.errno, e.strerror)
       raise
   except ValueError:
       print "Could not convert [%s] to an integer." % (nl)
   except:
       print "Unexpected error:", sys.exc_info()[0]
       raise

   
   print 'Done'
   return
   

Pyomo-Everest project 
=======================

It is a tool to support optimization modelling with the aid of Everest optimization services https://optmod.distcomp.org and 
Pyomo Python package, http://www.pyomo.org.

The tool enables solving independent mathematical programming problems in parallel in heterogeneous computing environment.

There are a number of services available at the https://optmod.distcomp.org. 
All of them are based on Everest toolkit http://everest.distcomp.org/. 
Each service, an Everest-application in Everest-terminology, is a front-end of a pool of solvers 
deployed and running on a number of various computing resources 
(desktops, standalone servers, clusters). 
This computing environment is extensible because the potential users can add their own computing resources to the 
optimization environment via the open source Everest agent, https://gitlab.com/everest/agent. 
On the other hand, user can call 
these services fron their applications via Everest Python API, https://gitlab.com/everest/python-api.

Now there are two basic services, which may be used for solve the set of mathematical programming problems in parallel:
1) https://optmod.distcomp.org/apps/vladimirv/solve-ampl-stub, Smirnov S., Voloshinov V., Sukhosroslov O. [Distributed Optimization on the Base of AMPL Modeling Language and Everest Platform](http://dx.doi.org/10.1016/j.procs.2016.11.037) // Procedia Computer Science, Vol. 101, 2016, pp. 313–322
2) https://optmod.distcomp.org/apps/vladimirv/SSOP, so called SSOP application. 

The 1st service looks an obsolete now due to extra load of Everest-server, 
because every problem "spawns" separate Everest Job (see Everest manuals for details).

The 2nd service inherits efficiency of the generic Parameter Sweep Everest application, http://everest.distcomp.org/docs/ps/.
A set of problems is processed in a single Job, each in a separate subtask. In addition PS provides a number of useful features:
flexible modification of data processing script via PLAN-file; input and outputs data in ZIP-files, which save Internet traffic; 
simple way to involve additional computing resources, including clusters and supercomputers. 
Due to the above reasons, it is strongly recommended to use SSOP in your research.

Installation and use of SSOP
--------------- 
It is assumed that you are a registered Everest user and a member of the **@optMod** users group (see https://optmod.distcomp.org/about)

1) Get a copy of Everests's Python API [it is Python 2.7, 3.12.9 (tested), compatible]:

   `wget https://gitlab.com/everest/python-api/raw/master/everest.py`
   
   or
   
   `git clone git@gitlab.com:everest/python-api.git`
2) Follow instruction https://gitlab.com/everest/python-api/blob/master/README.md 
   to install required Python secure connection packages.
3) Get pyomo-everest modulus:   

   `git clone git@github.com:distcomp/pyomo-everest.git`   
4) Get everest TOKEN-file in some way, e.g. following the README of Everest Python API test:
   
   `python everest.py get-token -u USER -l SOME_LABEL | tee .token`
   
5) Create some working directory to store NL-files, SOL-files, 
solver options file and all other auxiliary files, which will be created or downloaded during computing scenario with SSOP.

To use SSOP you need:

**1)** the following modules from **ssop** folder:
* **ssop_config.py**  with basic configuration parameters, including "default" pathes to TOKEN-file and working directory (*see example of everest.py call to get token in the comment*); 
IDs of Everest resources (see the `SSOP_RESOURCES` dictionary)  with solvers installed and supplied with proper Bash-scripts (**run-ipopt.sh, run-scip.sh**, may be **run-fscip.sh** etc.) might be used by SSOP-jobs and so on.
*  **ssop_session.py** implementing basic SSOP-abstraction of SSOP-session, inherits Everest-session 
in the context of SSOP usage and provides basic SSOP-functionality: authorization on Everest-server; opening Everest-session;
creating PLAN-file for the given list of NL-files (must be placed in the working directory); 
call SSOP application and obtaining resuts (will be placed in the working directory); clean working directory and deleting of Everest jobs, created during the session opened 
(DO NOT FORGET TO CLOSE SESSION, via **session.close()**, to avoid abnormal termination of your Python-application, 
see the end of **demoUseSsop.py**)    
* **demoUseSsop.py** presenting examples of SSOP usage, including call of different AMPL-compatible solvers 
(IPOPT, https://coin-or.github.io/Ipopt, and SCIP, https://scip.zib.de other solvers may be added soon)
* **testModel.py** with some simple nonconex mathematical programming problem, which is used in **demoUseSsop.py** demo-scenario

**2)** a couple of auxiliary modules from **asl_io** folder 
(actually, it is a modified content of https://github.com/Pyomo/PyomoGallery/tree/master/asl_io)
* **write.py** - a number of basic functions to create AMPL NL-files from Pyomo models (including "fast" NL-file writing, 
without SMAP-file creation)
* **read.py** - a number of basic function to read results of optimization in the form of AMPL SOL-file 
(with SMAP-creation in memory to load results in the model). See examples of usage in **demoUseSsop.py** 
(**makeNlFiles** and **checkResults** functions).

  
## The rest of instruction concers obsolete pyomo-everest features ##
1. Put everest.py to the $PE_PATH/everest_api folder (replace the old everest.py)

2. Add $PE_PATH to your $PATH 

3. Edit pe/pe_config.py 

#### Add your Everest login and password here to make token update automatically ####

EVEREST_LOGIN = 'YOUR_EVEREST_USER_LOGIN'

EVEREST_PASSW = 'YOUR_EVEREST_PASSWORD'

Now, you can run any Pyomo-Everest script by (YOU SHOULD USE python 2.7.*)
>runPyomoEverest.sh <yourPythonProgram>

E.g. go to examples/vvv64 and run
>runPyomoEverest.sh _SvF64a_everest.py


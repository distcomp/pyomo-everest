# -*- coding: UTF-8 -*-
from __future__ import division
from  numpy import *
from  time import *

from InData import *

from pyomo.environ import *
from pyomo.opt import SolverFactory

from Prep40 import * 
from Verif import *

from Lego import *

from Betta39  import *

#==pepepepepepepepepepepe==
from PyomoEverest  import *
#==========================


 
#fi = open ("mng_Rn2eq.txt")
#fi = open ("mng_Rn3de_TH.txt")
#fi = open ("mng_Rn.txt")
#fi = open ("mng_Kost.txt")
#fi = open ("mng_2eq_Rn(T,H).txt")
#fi = open ("mng_Bi(time).txt")
#fi = open ("mng_Bi(T,H).txt")
#fi = open ("mng_Rn1eq.txt")

#fi = open ("mng_VVfun.txt")
#fi = open ("mng_PLsrcWOdif.txt")
#fi = open ("mng_PLsrcDif.txt")
#fi = open ("mng_PL1.txt")

#fi = open ("mng_CallenF.txt")
#fi = open ("mng_CallenF-25.txt")
#fi = open ("mng_CallenNoB.txt")
#fi = open ("mng_CallenF-50.txt")
#fi = open ("mng_CallenNoB-50.txt")
#fi = open ("mng_CallenBar-25.txt")

#fi = open ("mng_VVfun25.txt")
#fi = open ("mng_PL25-25.txt")
#fi = open ("mng_PL50-25.txt")
#fi = open ("mng_PL50-50.txt")

#fi = open ("mngSin.txt")
#fi = open ("mng_CallenBar-50.txt")
#fi = open ("mng_CallenBar-50a.txt")
#fi = open ("mng_PL50-50.txt")
#fi = open ("mng_TamuraBar-50a.txt")

#fi = open ("mng_DE2_Rn(t).txt")
#fi = open ("mng_Bi(time).txt")

#fi = open ("mng_PH(t).txt")
#fi = open ("mng_Pb_Bi_PH(t).txt")

#fi = open ("mng_CallenSrc.txt")
#fi = open ("mng_CallenApp.txt")
#fi = open ("mng_CallenInt.txt")

fi = open ("mng_TamuraSrc.txt")
#fi = open ("mng_TamuraInt.txt")
#fi = open ("mng_TamuraApp.txt")


dimB = 2

Penal = []



Task = ""

PolyFunc   = "N"
#PolyPow = -1   
GridFunc   = "N"
DifEq1     = "N" 
DifEq2     = "N" 
DifEq2_TH  = "N"
DifEq3_TH  = 'N'
Plazma1    = 'N'

VarNormalization = "N"

DataPath        = ''  
ReadNameTblFrom = ""
WriteNameTblTo  = ""
ReadGridFrom = ""
WriteGridDataTo = ""
ReadGrid_VSfrom = ""
StabFile = ""
ReadDirection = 'X'
TranspGrid = 'N'
CVNoBorder = 'N'

#~ from InData import *

Datas = [ InData () ]


CVstep = 2             # разбиение на множества с шагом
CVpartSize = 0            # разбиение множества на части последовательно (кол-во частей)
CVside = 0

maxSigEst = 0           # оценка сигмы скольз. среднем

CVNumOfIter = 1
ExitStep = 1e-7

NDT = -99999.0

buf = ""

def readStr():
    global buf
    buf = buf.strip()
    print '\VBUF   |'+buf
    while 0== len(buf) or buf[0] == '#' :
        buf = fi.readline().strip() #(' \t\n')
        buf = buf.replace('\t',' ')
        print ' a !'+buf+'!'
    print ' b !'+buf+'!'
    buf = ' '.join(buf.split())   #   только одиночные пробелы !
    print ' c !'+buf+'!'
    if buf[0] == '"' :
        print " d !"+buf+'!'
        buf = buf[1:]
#        print "2 !"+buf+'!'
        p = buf.find('"')
        ret = buf[0:p];
        buf = buf = buf[p+1:];
#        print 'R +++!'+ret+'!'+buf+'!++++'
        return ret
    p = buf.find(' ')
    if p == -1 :   ret = buf; buf = ''
    else      :   ret = buf[:p]; buf = buf[p+1:]
#    print 'E +++!'+ret+'!'+buf+'!++++'
    return ret

def readList ( ) :
    global buf
    s =buf.split(']')
    buf = s[1];
    st = s[0]
    print '\nList',  st+']'
    s =st.replace(' ','').split('[')
    return s[1].split(',') 


def readFunc ( ) :               #   step vis min max    T(Ro{-25,0,0,1},Time)    T(Ro{-25,0,,1},Time)
    global buf
    s =buf.split(')')
    buf = s[1];
    st = s[0]
    print '\n\nFunc', st+')'
    s =st.replace(' ','').split('(')
    Datas[-1].V.append ( Vari(s[0]) ) # NAME F
    s =s[1]
#    print s
    while len(s)>0 :        # режим на аргументы
#        print "CY  ", s
        pc = s.find (',')
        if pc == 0 :  s = s[1:];  continue
        pp = s.find ('{')
#        print pc, pp
        if pp==-1 :                             # если нет { -  то арггументы через , 
            s = s.split(',')
#            print "PP   ", s
            for a in range(len(s)) :  Datas[-1].A.append (Arg(s[a]))
            return
        if pc!=-1 and pc < pp :                  #  , раньше чем { 
            Datas[-1].A.append (Arg(s[:pc]))
            s = s[pc+1:]
            continue;

        Datas[-1].A.append (Arg(s[:pp]))
        s = s[pp+1:]
#        print "ll",s
        ppz = s.find ('}')
        s1 = s[0:ppz]
#        print s1
        s1 = s1.split(',')
#        print s1
        Datas[-1].A[-1].step=float(s1[0])
        if len(s1) > 1 :  Datas[-1].A[-1].vis=float(s1[1])
        if len(s1) > 2 and len(s1[2]) > 0 :  Datas[-1].A[-1].min=float(s1[2])
        if len(s1) > 3 and len(s1[3]) > 0 :  Datas[-1].A[-1].max=float(s1[3])
        s = s[ppz+1:]
    return



while 1 :
#    global Data
#    if Data == 0 : Data = Datas[-1]
    qlf = readStr().upper()
    print qlf,

    if   qlf == "POLYFUNC"  :  PolyFunc = "Y";  Datas[-1].PolyPow = int(readStr()); #Data.dim = dim=2
    elif qlf == "TASK"    :  Task = readStr()
    elif qlf == "FUNC"    :  readFunc()
    elif qlf == "DIMBETTA"    : dimB = int(readStr())
    elif qlf == "PENALTY"    :
                                pen = readList()
                                for p in pen : Penal.append(float(p)) 
    
    elif qlf == "POLYPOW"   :                   Datas[-1].PolyPow = int(readStr()); #Data.dim = dim=2
    elif qlf == "GRIDFUNC"   :  GridFunc = "Y"; dimB = 1; Task = 'GridFunc'
    elif qlf == "DIFEQ2"      :  DifEq2    = "Y";  dimB = 1
    elif qlf == "DIFEQ1"      :  DifEq1    = "Y";  dimB = 1
    elif qlf == "DIFEQ2_TH"   :  DifEq2_TH = "Y";  dimB = 1
    elif qlf == "DIFEQ3_TH"   :  DifEq3_TH = "Y";  dimB = 1
    elif qlf == "PLAZMA1"   :  Plazma1 = "Y";  dimB = 1

    elif qlf == "VARNORMALIZATION" :  VarNormalization = "Y";

    elif qlf == "DATAPATH"     :  DataPath  = readStr()
    elif qlf == "READNAMETBLFROM" :  ReadNameTblFrom  = readStr()
    elif qlf == "WRITENAMETBLTO"  :  WriteNameTblTo   = readStr()
    elif qlf == "READGRIDFROM"    :  ReadGridFrom     = readStr()
    elif qlf == "WRITEGRIDDATATO" :  WriteGridDataTo  = readStr()
    elif qlf == "READGRID_VSFROM" :  ReadGrid_VSfrom  = readStr()
    elif qlf == "TRANSPGRID"      :  TranspGrid  = 'Y'
    elif qlf == "CVNOBORDER"      :  CVNoBorder  = 'Y'

    elif qlf == "STABFILE"        :  StabFile         = readStr()

    elif qlf == "NAMEF"     :  Datas[-1].V.append ( Vari(readStr()) )
    elif qlf == "ADDCOL"    :  Datas[-1].Col.append ( Col(readStr()) )

    elif qlf == "NAMEX"     :  Datas[-1].A.append ( Arg(readStr()) )
    elif qlf == "NAMEY"     :  Datas[-1].A.append ( Arg(readStr()) )
    elif qlf == "STEPX"     :  Datas[-1].A[0].step = float(readStr()) 
    elif qlf == "STEPY"     :  Datas[-1].A[1].step = float(readStr())
    elif qlf == "VISX"      :  Datas[-1].A[0].vis  = float(readStr())
    elif qlf == "VISY"      :  Datas[-1].A[1].vis  = float(readStr())
    elif qlf == "ADDARG"    :  Datas[-1].A.append(Arg(readStr())); Datas[-1].A[-1].step=float(readStr()); Datas[-1].A[-1].vis=float(readStr())

    elif qlf == "MINX"      :  Datas[-1].A[0].min  = float(readStr()) 
    elif qlf == "MINY"      :  Datas[-1].A[1].min  = float(readStr())
    elif qlf == "MAXX"      :  Datas[-1].A[0].max  = float(readStr())
    elif qlf == "MAXY"      :  Datas[-1].A[1].max  = float(readStr())
    elif qlf == "RECTANGLE" :
                               Datas[-1].A[0].min = float(readStr()); Datas[-1].A[1].min =float(readStr())
                               Datas[-1].A[0].max = float(readStr()); Datas[-1].A[1].max =float(readStr())
    elif qlf == "NODATA"    :  Datas[-1].NDT       =NDT       = float(readStr())
    elif qlf == "COND"      :  Datas[-1].C.append ( Cond(readStr(),readStr(),float(readStr()) ) )

    elif qlf == "BETTA"     :  betta1 =betta2 = float(readStr()); Penal.append(betta1); Penal.append(betta2)
    elif qlf == "BETTA1"    :  betta1         = float(readStr()); Penal.append(betta1)
    elif qlf == "BETTA2"    :  betta2         = float(readStr()); Penal.append(betta2)
    elif qlf == "CVNUMOFITER" :  CVNumOfIter = int(readStr())
    elif qlf == "EXITSTEP"    :  ExitStep = float(readStr())
    elif qlf == "CVSTEP"     :  CVstep  = int(readStr())
    elif qlf == "CVPARTSIZE" :  CVpartSize = int(readStr());  CVside = float(readStr())

    elif qlf == "MAXSIGEST" :  maxSigEst = float(readStr());
    elif qlf == "EOD" or  qlf == "EOF" :
        if ReadNameTblFrom != "" :
                            Datas[-1].ReadTbl    ( ReadNameTblFrom, DataPath )
                            Datas[-1].CheckNames ()
        elif ReadGridFrom != "" :     Datas[-1].ReadGrid   ( ReadGridFrom, DataPath )
        elif ReadGrid_VSfrom != "" :
                            Datas[-1].ReadGrid_VS( ReadGrid_VSfrom, DataPath, ReadDirection )
                            Datas[-1].CheckNames ()

        Datas[-1].ClareTbl( )

        if maxSigEst :        Datas[-1].SigEst ( maxSigEst )

        if WriteNameTblTo != "" :    Datas[-1].WriteTbl ( WriteNameTblTo )
        
#        Datas[-1].V.append ( Vari('Bi') )      #  for  Pb + Bi
#        Datas[-1].V[1].num = 11
        
        Datas[-1].Normalization ( VarNormalization )

##        w1 = 0.1851  # must be                #  for  Pb + Bi
#        w1 = 0.15     # betta
#        w2 = 1-w1
#        for r in range(Datas[-1].tbl.shape[0]) :
#            Datas[-1].tbl[r,Datas[-1].V[0].num] =  w1*Datas[-1].tbl[r,Datas[-1].V[0].num] \
#                                                 + w2*Datas[-1].tbl[r,Datas[-1].V[1].num]
#        Datas[-1].SigEst ( maxSigEst )
##        Datas[-1].WriteTbl ( 'a.a' )

        print "NoR=", Datas[-1].NoR
        
        if qlf == "EOF"       :  break 
        Datas.append ( InData() )
        ReadNameTblFrom = ''
        ReadGridFrom    = ""
        ReadGrid_VSfrom = ""

#        print "LL", len(Datas)
#        Data = 0 # Datas[-1]
    else :  print "********* Не понял: ", qlf
fi.close()
print '\n\n'

Data = Datas[-1]
Data = Datas[0]


#~ from pyomo.environ import *
#~ from pyomo.opt import SolverFactory

opt = SolverFactory('ipopt') #Ignore "Failed to create solver ..."
#opt = SolverFactory('ipopt_old')
#opt = SolverFactory('ipopt3_12_4')
opt.options["print_level"] = 4
opt.options['warm_start_init_point'] = 'yes'
opt.options['warm_start_bound_push'] = 1e-6
opt.options['warm_start_mult_bound_push'] = 1e-6
opt.options['mu_init'] = 1e-6
# copy Solver.options to file 
#==pepepepepepepepepepepe==
writeIpoptOptionsFile(opt.options)
#==========================

               
#~ quit()


#~ from Prep40 import * 
#~ from Verif import *

if CVpartSize :  vSet, mSet = makePartSets ( Data.NoR, CVpartSize, CVside )
else:            vSet, mSet = makeStepSets ( Data.NoR, CVstep )

sR  = Data.sR  #range ( NoR )

#            sys.exit()   raw_input
#            print '\n', len(Gr.grd0), dir(Gr.grd0), '\n', dir(Gr.grd0.index_set())

#~ from Lego import *

if    'GridFunc'    == Task :    from T_GridFunc     import *
elif  'DE2_Rn(t)'  == Task :     from T_Radon        import *
elif  'Plazma_Src'  == Task :    from T_Plazma_Src   import *
elif  'Plazma_K(T)' == Task :    from T_Plazma_K_T   import *
elif  'CallenNoB'  == Task :     from T_CallenNoB   import *
elif  'CallenBar'  == Task :     from T_CallenBar   import *
elif  'TamuraBar'  == Task :     from T_TamuraBar   import *
elif  'PlazmaSrc'  == Task :     from T_PlazmaSrc   import *
elif  'Pb_Bi_PH(t)'== Task :     from T_Pb_Bi_PH   import *
else :
  def createGr ( Datas, Penal ) :

      bet1 = Penal[0]
      bet2 = Penal[1]
#      bet3 = Penal[2]
#      bet4 = Penal[3]
      Gr = ConcreteModel()
      Gr.mu  = Param (sR, mutable=True, initialize = 1 )   ##  int???
      Gr.F = []
      
      if PolyFunc == "Y":             #################    PolyFunc
#            addPolyFunc ( Gr, [Data.A[0], Data.A[1]], Data.V[0], PolyFunc )
            addPolyFunc ( Gr, Data.A, Data.V[0], PolyPow )
            Var_init_fix (Gr) 
            if len(Data.A) == 1:
                print "grdX", Gr.F[0].Ar[0].Ub
                def obj_expression(G):
                  return (  bet1**4 / Gr.F[0].Nxx  / (1./Gr.F[0].Ar[0].Ub)**4 * Gr.F[0].sumXX ( ) 
                          + Gr.F[0].MSD ( ) )
            else :    
                print "grdX", Gr.F[0].Ar[0].Ub, "grdY", Gr.F[0].Ar[1].Ub
                def obj_expression(G):
                  return (  bet1**4 / Gr.F[0].Nxx  / (1./Gr.F[0].Ar[0].Ub)**4 * Gr.F[0].sumXX ( ) 
                          + bet2**4 / Gr.F[0].Nyy  / (1./Gr.F[0].Ar[1].Ub)**4 * Gr.F[0].sumYY ( ) 
                          + bet1**2 * bet2**2 * 2. / Gr.F[0].Nxy * 0.25 / (1./Gr.F[0].Ar[0].Ub)**2
                                            / (1./Gr.F[0].Ar[1].Ub)**2 * Gr.F[0].sumXY ( ) 
                          + Gr.F[0].MSD ( ) )

         
      Gr.OBJ = Objective(rule=obj_expression)
      return Gr


#~ from STAB      import *

Parallel = 'Y' # VVV

def get_sigCV (Penal) :

    Gr =  createGr ( Datas, Penal )

    if StabFile != "" :
        nls, nlEND, p_1_NoR, symbol_map = PrepStab ( Gr, StabFile, Data.NoR ) 


    sigCV = 0.0
    nCV = 0
    sigCV1 = 0.0
    nCV1 = 0
    partF = 0.0
    #Gr.preprocess()
    star = clock()

    sym_maps = []
    resultss = []
    
    if Parallel == 'Y' :                                               # VVV
		
        __peProblems = []                                     # __pe - prefix for Pyomo&Everest stuff
        
        for k in range( len(vSet) ) :
            for s in mSet[k] : Gr.mu[s]=0
            pName = "abc007"+str(k)
            _, smap_id = Gr.write( pName + ".nl", format=ProblemFormat.nl)  # создаем стаб
            symbol_map = Gr.solutions.symbol_map[smap_id]
            sym_maps.append(symbol_map)
            for s in mSet[k] : Gr.mu[s]=1
            print "make", "abc007"+str(k)+".nl"
            __peProblems.append(pName)
            
        #~ print __peProblems

        #===== solve in parallel ===========
        peSolveListOfStubs(__peProblems)
        #===================================
        
        for k in range( len(vSet) ) :                                               # обрабатываем решения
            #~ subprocess.check_call('ipopt -s ' + "abc007"+str(k)+".nl", shell=True)

            with ReaderFactory(ResultsFormat.sol) as reader:
                results = reader( "abc007"+str(k)+".sol" )
            results._smap = sym_maps[k]

            if results.solver.termination_condition != TerminationCondition.optimal:
                raise RuntimeError("Solver did not terminate with status = optimal")
            resultss.append(results)
            print "solve", "abc007"+str(k)+".nl"
            
        quit()

                
    for k in range( len(vSet) ) :

        if DifEq2_TH == "Y" and k==0 :  continue
            
        for s in mSet[k] : Gr.mu[s]=0
        #results = opt.solve(Gr, tee=True, keepfiles=True)

        if Parallel == 'Y' :                                     # VVV
            results = resultss[k]                                  #  для считывания результатов
        elif StabFile != "" :
            results = makeStab_solve ( StabFile, Gr, nls, nlEND, p_1_NoR, Data.NoR, symbol_map ) 
        else:
#            opt.options["tol"] = 1e-9 
#            opt.options["print_level"] = 4
#            opt.options['warm_start_init_point'] = 'yes'
#            opt.options['warm_start_bound_push'] = 1e-6
#            opt.options['warm_start_mult_bound_push'] = 1e-6
#            opt.options['mu_init'] = 1e-6
            
            results = opt.solve(Gr, tee=False)
#            results = opt.solve(Gr, tee=True)
#opt.solve(model,keepFiles=keepfiles,tee=stream_solver)


        Gr.solutions.load_from(results)
        print k,  
        if str(results.solver.termination_condition) != 'optimal' :
            print "Stst:", results.solver.termination_condition, '\n'
#        print k, "Stst:", results.Solution.Status,
        
        for s in mSet[k] :  Gr.mu[s]=1
        

        sigCVpart = sum ( (Gr.F[0].tbl[s,Gr.F[0].Va.num]!=NDT) * Gr.F[0].delta(s)()**2 for s in vSet[k] )
        nCVpart   = sum ( (Gr.F[0].tbl[s,Gr.F[0].Va.num]!=NDT) for s in vSet[k] )
        print sqrt( sigCVpart / nCVpart )

        if  CVNoBorder == 'Y' :          #  на границах по ро не проверяем
            if k != 0 and k!= len(vSet)-1 :        
                sigCV += sigCVpart
                nCV   += nCVpart
                print "+",k
        elif (    DifEq2 == "Y"
             or Task == 'DE2_Rn(t)'
             or DifEq2_TH == "Y"
             or DifEq3_TH == "Y" ) : 
           sigCV  += (1-Penal[1])*sum ( (Gr.F[0].tbl[s,Gr.F[0].Va.num]!=NDT) * Gr.F[0].delta(s)()**2
                          for s in vSet[k] )
           nCV    += (1-Penal[1])*sum ( (Gr.F[0].tbl[s,Gr.F[0].Va.num]!=NDT) for s in vSet[k] )
           sigCV1 += Penal[1]*sum ( (Gr.F[1].tbl[s,Gr.F[1].Va.num]!=NDT) * Gr.F[1].delta(s)()**2
                          for s in vSet[k] )
           nCV1   += Penal[1]*sum ( (Gr.F[1].tbl[s,Gr.F[1].Va.num]!=NDT) for s in vSet[k] )
        else :
           sigCV += sigCVpart
           nCV   += nCVpart
           
    if (    DifEq2 == "Y"
         or Task == 'DE2_Rn(t)'
         or DifEq2_TH == "Y"
         or DifEq3_TH == "Y" ) :
        print "Части",  sqrt( 1./nCV * sigCV ), sqrt( 1./nCV1 * sigCV1 )
        sigCV += sigCV1
        nCV += nCV1
#    else :
 #       nCV = Data.NoR
    sigCV = sqrt( sigCV / nCV   )
    print "Time ", clock()-star
    return sigCV, sigCV, partF/len(vSet)



#~ from Betta39  import *

if WriteGridDataTo != "" :
    Gr =  createGr ( Datas, Penal )
    Data.SaveGrid ( Gr.F[1],'' )
    Gr.F[1].SaveSol('a.sol')
    Gr.F[1].SavePoints()
    a=1/0

#    if Gr.F[0].dim == 2 :       Data.SaveGrid ( Gr.F[0],'' )
#    Gr.F[0].SaveSol('a.sol')
#    Gr.F[0].SavePoints()
    del Gr

sigCV_W_N = 0
for iter in range(1,CVNumOfIter+1) :
    print "\nM ITER ", iter,  "Penal", Penal 
    sigCV, sigCV_W_N, partF = get_sigCV (Penal)
    print "      sigCV", sigCV, "sigNoNor", sigCV_W_N, "partF", partF

#    Penal[2],Penal[3], step = getBetta2 ( sigCV, Penal[2],Penal[3], dimB )
    Penal[0],Penal[1], step = getBetta2 ( sigCV, Penal[0],Penal[1], dimB )
    if step <= ExitStep: break;



if CVNumOfIter > 0 :
    Penal[0],Penal[1] = getMinBetta ()
print "\nPenalty", Penal
print "sigNor", sigCV_W_N/Data.V[0].sigma

## Gr =  makeGr (bet1, bet2)
Gr =  createGr ( Datas, Penal )
#Gr =  makeGr (Penal)

star = clock()
results = opt.solve(Gr)
print "  Object: ", results.solver.termination_condition, 'Time', clock()-star
Gr.solutions.load_from(results)

Obj = Gr.OBJ()

print '\nITOGO Obj', Obj
for f in Gr.F :
    print  "sig", f.Va.sigma, "Cmp",
    if f.dim == 1 :   print  f.Complexity ( [Penal[0]] )(),
    else :            print  f.Complexity ( [Penal[0], Penal[1]] )(),
##    if f.dim == 1 :   print  f.Complexity ( [bet1] )(),
##    else :            print  f.Complexity ( [bet1, bet2] )(),
    if str(type(f.tbl)) == '<type \'int\'>' : print ''
    elif f.Va.num == -99 : print ''
    else :
        print  "MSD", f.MSDno_mu( )(), "sqrt", sqrt(f.MSDno_mu( )()),"%", sqrt(f.MSDno_mu( )())/f.Va.sigma * 100


if Task == "Plazma1" or Task == "Plazma2" : 
    print "Tax", Gr.F[4].sumXX ( ) ()
    for x in Gr.F[4].Ar[0].NodS :
             print sum (  Gr.F[4].neNDT[x] *  Gr.F[4].derivXX1 ( x )()  ) 
                       

    
    if  Task == "Plazma2" :
         print "   NVZ", sum ( Gr.grd5[r,t].value**2 for r in Gr.F[5].Ar[0].mNodSm for t in Gr.F[5].Ar[1].mNodSm )

    MSD = Gr.F[0].MSDno_mu( )()
    for f in range(4) :
        print f, Gr.F[f].MSDno_mu( )(), "sqrt", sqrt(Gr.F[f].MSDno_mu( )()), \
            "sig", Gr.F[f].Va.sigma, "%", sqrt(Gr.F[f].MSDno_mu( )())/Gr.F[f].Va.sigma * 100
    print 'Hrel', Gr.Hrel()


else:
    MSD = Gr.F[0].MSDcheck( )()

if (    DifEq2 == "Y"
     or DifEq2_TH == "Y"
     or DifEq1 == "Y"  ) :
    MSD1 = Gr.F[1].MSDcheck( )()
    print "%ПР", (MSD+MSD1)/Obj*100, "Obj", Obj, "откл", sqrt(MSD), sqrt(MSD1)
else:
    print "%ПР", MSD/Obj*100, "Obj", Obj, "откл.норм", sqrt(MSD), "откл.исх", \
          sqrt(MSD)*Data.V[0].sigma  #, sqrt(MD1)*Data.V[1].sig
#    print 'Gr.PbBi', Gr.PbBi()
#else :
#    MD = Gr.F[0].MSD ()()
#    if dim==1 : MD = MSD1 ( Gr, Gr.F[0] )()
 #   else :      MD = Gr.F[0].MSD ()()
#    print Obj, "откл.норм", sqrt(MD), "откл.исх", sqrt(MD)*Data.V[0].sig


for f in range(len(Gr.F)) :
    if Gr.F[f].dim == 2 :       Gr.F[f].SaveGrid ( TranspGrid, '' )
    Gr.F[f].SaveSol('')
    Gr.F[f].SavePoints()

#if len(Data.Col) :  Data.SaveCols()  
Gr.F[0].SaveDeriv ( "" )

print_res(Gr, Penal)

print "EoP"




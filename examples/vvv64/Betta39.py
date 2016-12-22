# -*- coding: utf-8 -*-
from  numpy import *
from pyomo.environ import *
from pyomo.opt import SolverFactory

fb = []             #  fun, betta1, betta2
F  = 0
B1 = 1
B2 = 2

def getMinBetta () :
    return fb[-1][B1], fb[-1][B2] 

step = 0.0
reg  = 1.0
progn_incr = 0.0
search_mod = ""

dirX = dirY = 0

#xP = [0, 1, 0, 2, 0, 1]
#yP = [0, 0, 1, 0, 2, 1]
xP = [1, 0, 2, 0, 1]
yP = [0, 1, 0, 2, 1]

def pol ( C, X, Y, I ) :
#    global xP, yP
    return sum ( C[i]*X**xP[i]*Y**yP[i] for i in range(I) )

def CreateMatr ( fb, q, Nfb, N ) :
    A = zeros( (N,N), float64 )
    B = zeros(  N,    float64 )
    nor =  sum( 1.0/(sqrt((fb[n][B1]-fb[-1][B1])**2+(fb[n][B2]-fb[-1][B2])**2))**q for n in range (Nfb-1) )  
    for k in range(N) :
        for p in range(N) :
            A[k,p] = 1/nor *sum (  (fb[i][B1]-fb[-1][B1])**xP[k]
                                  *(fb[i][B2]-fb[-1][B2])**yP[k]
                                  *(fb[i][B1]-fb[-1][B1])**xP[p]
                                  *(fb[i][B2]-fb[-1][B2])**yP[p]
                                  /(sqrt((fb[i][B1]-fb[-1][B1])**2+(fb[i][B2]-fb[-1][B2])**2))**(2+q) 
                            for i in range(Nfb-1) )
    for k in range(N) :
        B[k] = 1/nor *sum (  (fb[i][B1]-fb[-1][B1])**xP[k]
                            *(fb[i][B2]-fb[-1][B2])**yP[k]
                            *(fb[i][F]-fb[-1][F])
                            /(sqrt((fb[i][B1]-fb[-1][B1])**2+(fb[i][B2]-fb[-1][B2])**2))**(2+q) 
                      for i in range(Nfb-1) )
    return A, B             

def solveLE ( A, B, reg ) :
    N = 5
    A1 = zeros( (N,N), float64 )
    for k in range(N) :
        for p in range(N) :
            A1[k,p] = A[k,p]
    for k in range(2,5) : A1[k,k] += reg
    return linalg.solve(A1,B)


def getBetta2 ( fun, bet1, bet2, dim ) :  # fb - last элемент содержит min 
#    global step, reg, progn_incr, abs_obj, search_mod, dirX, dirY
    global step, progn_incr, search_mod, dirX, dirY

    if len(fb)==0: 
        step = sqrt ( 0.5*(bet1**2 + bet2**2) ) * 0.005
        dirX = -1
        dirY =  0
        search_mod = ""
        reg = 1.0e-5

    reg = 10000.0
        

    df_db = 0;
    if len(fb) > 0:
        incr = fun - fb[-1][F]       
        df_db = incr / sqrt( (bet1-fb[-1][B1])**2 + (bet2-fb[-1][B2])**2 )
    print "BSTART fb", len(fb), "bet", bet1, bet2, "fun", fun, "s_mod", search_mod, "df/db", df_db


    if  len(fb) >= 4 :     #  searching for reg  так чтобы новая точка попадала в прогноз  
            A,B = CreateMatr ( fb, 2, len(fb), 5 )   # новую еще не добавили
            minReg = reg = 1e-7* sum (  abs(A[k,p])  for k in range(5) for p in range(5) )
            C = solveLE ( A, B, reg )
            minV = abs(fun-fb[-1][F]-pol( C, bet1-fb[-1][B1], bet2-fb[-1][B2], 5 ))
            print "*  reg start " , reg, minV,
            reg *= 1.1 
            C = solveLE ( A, B, reg )
            tmpV = abs(fun-fb[-1][F]-pol( C, bet1-fb[-1][B1], bet2-fb[-1][B2], 5 ))
#            print "** reg" , reg, tmpV 
            if (tmpV < minV):  malt = 2 #10**0.5
            else :             malt = 1./2. #10**0.5
            for r in range(30) :
                reg *= malt 
                C = solveLE ( A, B, reg )
                tmpV = abs(fun-fb[-1][F]-pol( C, bet1-fb[-1][B1], bet2-fb[-1][B2], 5 ))
#                print "***reg" , reg, tmpV, fun-fb[-1][F]-pol( C, bet1-fb[-1][B1], bet2-fb[-1][B2], 5 ) 
                if (tmpV < minV):
                    minV = tmpV
                    minReg = reg
                else : break
            reg = minReg
            print "min", r, reg, minV #, "C",
#            for c in range(5) : print C[c],
#            print ""

    fb.append([ fun, bet1, bet2 ])      #  добавляем точку

    up = False
    if len(fb) > 1 :
        if fb[-1][F] > fb[-2][F] :     #   fb - last элемент содержит min 
            sw = fb[-2]                 #  min всплывает
            fb[-2] = fb[-1]
            fb[-1] = sw
            up = True
        else :  print "*************** MIN *****************" 

    if   search_mod == "" : 
         search_mod =  "1" 
    elif search_mod == "1" :
#         if dim ==1 : search_mod =  "2d" 
#         if dim ==2 : 
             search_mod =  "2"
             dirX =  0
             dirY = -1
    elif search_mod == "2" :
         search_mod =  "2d"            # search for direction
    elif search_mod == "2d" :
         if up :
             search_mod =  "2ds"       # search for direction and step
             step *= .5 
         else :                        # не переходим к расчету шага пока не упремся в подъем
             step *= 5 
            
    if len(search_mod) >= 2 :       # "2d" или "2ds"    
            A,B = CreateMatr ( fb, 2, len(fb), 5 ) ######################
            C = solveLE ( A, B, reg )
            print "2d  ", 
            for c in range(5) : print C[c],
            print ""
            dirX = - C[0] / sqrt(C[0]**2+C[1]**2)
            dirY = - C[1] / sqrt(C[0]**2+C[1]**2)

    if  search_mod == "2ds" :    
            quol = abs( (progn_incr-incr)/sqrt(0.5*progn_incr**2 + 0.5*incr**2) )
            step = abs ( step )
            if   quol > 0.5: step *= 0.2;  
            elif quol > 0.3: step *= 0.5
            elif quol < 0.05:
                if quol > 1e-20 : step *= sqrt(0.3/quol)
                else :            step *= 10
            elif quol < 0.1: step *= 1.5
            print "2ds progn", progn_incr, incr, quol, "new step", step

    if step > 0.75*abs(fb[-1][B1]):     # !!!!!!!!!!
            step = 0.75*abs(fb[-1][B1])
            print "CUT step", step
#    if step > 0.75*abs(fb[-1][B2]):     # !!!!!!!!!!
    if step > 0.75*abs(fb[-1][B2]) and dim == 2 :     # !!!!!!!!!!
            step = 0.75*abs(fb[-1][B2])
            print "CUT step", step
    if len(search_mod) >= 2 :                 # "2d" или "2ds"   
        for pi in range(5) :
            progn_incr = pol( C, dirX*step, dirY*step, 5 )
            if progn_incr <= 0 : break
            else :               step /= 2
        
    bet1 = fb[-1][B1] + dirX*step
    bet2 = fb[-1][B2] + dirY*step
    print "B END st", step, "  bet", bet1, bet2, " progn_incr", progn_incr
#    if dim ==1 : return bet1, bet1
#    else:        return bet1, bet2
    return bet1, bet2, step



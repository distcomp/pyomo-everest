# -*- coding: utf-8 -*-
from __future__ import division
from  numpy import *
from pyomo.environ import *
#from pyomo.opt import SolverFactory

from InData import *
#from GlobName import * 

import copy



class Fun :                  # 
    def __init__ (self ) :
        self.type  = " "
        self.dim   = 0
        self.Va    = 0
        self.Ar    = [] 
        self.grd   = grd
        self.neNDT = 0
        self.Nxx   = 0
            
    def Ini (self, Data, type, Va, Ar, G, grd, neNDT, der2 ) :
        self.Dat   = Data
        self.NoR   = Data.NoR
        self.sR    = Data.sR
        self.tbl   = Data.tbl
        self.NDT   = Data.NDT
        self.type  = type
        self.dim   = len(Ar)
        self.Va    = Va
        self.Ar    = Ar     
        self.G     = G
        self.grd   = grd
        self.neNDT = neNDT
        self.Nxx   = der2[0]
        if self.dim == 2 :
            self.Nyy   = der2[1]
            self.Nxy   = der2[2]
            print "Add "+type, Va.name+'('+Ar[0].name+','+Ar[1].name+')', Ar[0].Ub, Ar[1].Ub, \
                  "Nxx",der2[0],der2[1],der2[2]
        else :
            print "Add "+type, Va.name+'('+Ar[0].name+')', Ar[0].Ub, "Nxx",der2[0]

    def FixAll (self) :
        if self.type == 'p' :
            for p in self.PolyR :  self.grd[p].fixed = True 
            print "FixAll Poly" 
        elif self.dim == 1 :
            for x in self.Ar[0].NodS :  self.grd[x].fixed = True 
            print "FixAll 1" 
        else :      
            for x in self.Ar[0].NodS :  
              for y in self.Ar[1].NodS :  self.grd[x,y].fixed = True
            print "FixAll 2" 

    def Fix (self) :
        if self.type == 'p' : return
        if self.dim == 1 :
            for x in self.Ar[0].NodS :  
                if not self.neNDT[x] :
                  self.grd[x].value = self.NDT
                  self.grd[x].fixed = True 
        else :      
            for x in self.Ar[0].NodS :  
              for y in self.Ar[1].NodS :  
                if not self.neNDT[x,y] :
                  self.grd[x,y].value = self.NDT
                  self.grd[x,y].fixed = True

    def Ftbl ( self, n ) : pass
    def F ( self, ArS ) :  pass
    def sumXX ( self ) :   pass
    def SaveSol ( self, fName ) :  pass

    def delta( self, n ) :
        return	 self.tbl[n,self.Va.num] - self.Ftbl ( n ) 
    def MSD ( self ) : 
            return  1. / self.NoR * sum   (  self.G.mu[n] * self.delta(n)**2  for n in self.sR )

    def MSDcheck(self) :
            return  1./self.Va.NoR * sum ( (self.tbl[n,self.Va.num]!=self.NDT)
                                           * self.G.mu[n] * self.delta(n)**2
                                     for n in self.sR )
    def MSDno_mu ( self ) : 
        return  1. / self.NoR * sum   ( self.delta(n)**2  for n in self.sR )

    def Complexity ( self, bets ) :
            if self.dim == 1 :
              return    bets[0]**4 / self.Nxx  / (1./self.Ar[0].Ub)**4 * self.sumXX ( )
            else:
              return (  bets[0]**4 / self.Nxx  / (1./self.Ar[0].Ub)**4 * self.sumXX ( ) 
                      + bets[1]**4 / self.Nyy  / (1./self.Ar[1].Ub)**4 * self.sumYY ( ) 
                      + bets[0]**2 * bets[1]**2 * 2. / self.Nxy * 0.25 / (1./self.Ar[0].Ub)**2
                                        / (1./self.Ar[1].Ub)**2 * self.sumXY ( )
                     )   

    def SavePoints ( self ) :
        for a in self.Ar :
            if a.num < 0 : print "num < 0  arg=",  a.name;  return;
            
        if self.dim == 1 : fName = "SvF_"+self.Va.name + "(" +self.Ar[0].name+ ").txt"
        else :  fName = "SvF_"+self.Va.name + "(" +self.Ar[0].name+ "," +self.Ar[1].name+ ").txt"
        fi = open ( fName, "w")
        for a in self.Ar :  fi.write ( a.name + "\t" )      # Names args
        fi.write ( self.Va.name + '_SvFs' ) # решение
        if self.Va.num >= 0 : fi.write ( "\t" + self.Va.name )  # точки
        for c in range(len(self.Dat.Col)) :  fi.write ( "\t" + self.Dat.Col[c].name)
         
        for n in self.sR :                                           # Data
            fi.write ( "\n" )             
#            for a in self.Ar : fi.write ( str( a.min + a.step * self.tbl[n,a.num] ) + '\t' )
            for a in self.Ar : fi.write ( str( a.min + self.tbl[n,a.num] ) + '\t' )
            fi.write (  str( self.Va.avr + self.Ftbl(n)() ) )
            if self.Va.num >= 0 : 
                fi.write ( '\t'+ str( self.Va.avr + self.tbl[n,self.Va.num] ) )

            for c in range(len(self.Dat.Col)) : fi.write ( "\t"+ str( self.tbl[n,self.Dat.Col[c].num] ) )
        print "SavePoints"

  
# GRID 1  ***********************************************************
class gFun1(Fun) :
    def __init__ (self, Data, G, grd, Va, Ar1, neNDT, Nxx ) :
        self.Ini ( Data, 'g', Va, [Ar1], G, grd, neNDT, [Nxx] ) 

    def Ftbl ( self, n ) :
#        x = self.tbl[n,self.Ar[0].num]; 
        x = self.tbl[n,self.Ar[0].num]/self.Ar[0].step;
        Xi = floor ( x );  
        if Xi==self.Ar[0].Ub : Xi=self.Ar[0].Ub-1     # убирает данное с (не 0) границы.
        dx = x-Xi; 
        return  self.grd[Xi] * ( 1 - dx )  + self.grd[Xi+1] * ( dx )

    def F ( self, ArS ) :  # не проверенно
        x = ArS[0]/self.Ar[0].step;
        Xi = floor ( x ); 
        if Xi==self.Ar[0].Ub : Xi=self.Ar[0].Ub-1     # убирает данное с (не 0) границы.
        dx = x-Xi; 
        return  self.grd[Xi] * ( 1 - dx )  + self.grd[Xi+1] * ( dx )


#    def delta1(n, Pa) :
#        return (  self.tbl[n,Pa.Va.num] - interPol1a ( Pa, self.tbl[n,Pa.Ar[0].num] ) )

    def sumXX ( self ) :
        return  sum ( self.neNDT[x-1] * self.neNDT[x] * self.neNDT[x+1] * 
                     ( self.grd[x-1]-2*self.grd[x]+self.grd[x+1] )**2  
		    for x in self.Ar[0].mNodSm ) 
    def SaveSol ( self, fName ) :
        A = self.Ar[0]
        V = self.Va
        if fName == '' :  fName = "SvF_"+V.name + "(" +A.name+ ").sol"
        fi = open ( fName, "w")
        fi.write ( A.name + '\t' + V.name + "_SvF\n")
        for i in A.NodS :
            print >> fi, str(A.min + A.step*i), "\t" + "%20.16g" % ((V.avr + self.grd[i]()))    #  значения
        fi.close()
        print "END of SaveSol"

    def ReadSol ( self, ReadFrom ) :
        if ReadFrom == '' :
            ReadFrom = "SvF_"+self.Va.name + "(" +self.Ar[0].name+ ").sol"
        fi = open ( ReadFrom, "r")
        print "ReadSol from", ReadFrom,  fi.readline().split(),
        tb = loadtxt (fi,'double')
        print "shape", tb.shape

        for j in self.Ar[0].NodS :
                self.grd[j].value = (tb[j*(tb.shape[0]-1)/self.Ar[0].Ub,1]-self.Va.avr)  #  значения в новых узлах 
        fi.close()

        
    def SaveDeriv ( self, fName ) :
        A = self.Ar[0]
        V = self.Va
        if fName == '' :  fName = "SvF_"+V.name + "(" +A.name+ ").der"
        fi = open ( fName, "w")
        fi.write ( A.name + '\t' + V.name + "_der\n")
        for i in A.mNodSm :
            fi.write ( "\n" + str(A.min + A.step*i)
                     + "\t" + str( (self.grd[i+1]()-self.grd[i-1]()) / (2*A.step) ) )
        fi.close()
        print "END of SaveDeriv"

    def InitByData ( self ) :
        if str(type(self.tbl)) == '<type \'int\'>' : return
        if self.Va.num == -99 : return
        print  "self.NDT",  self.NDT
        for m in self.sR :
            if self.tbl[m,self.Va.num] == self.NDT : continue
            self.grd[floor(0.499999999+self.tbl[m,self.Ar[0].num]/self.Ar[0].step)]  \
                            = self.tbl[m,self.Va.num]
            



#  GRID 2  *************************************************************
class gFun2(Fun) :                  # 
    def __init__ (self, Data, G, grd, Va, Ar1, Ar2, neNDT, Nxx, Nyy, Nxy ) :
        self.Ini ( Data, 'g', Va, [Ar1, Ar2], G, grd, neNDT, [Nxx, Nyy, Nxy] )

    def Ftbl ( self, n ) :
        x = self.tbl[n,self.Ar[0].num]/self.Ar[0].step;
        y = self.tbl[n,self.Ar[1].num]/self.Ar[1].step
        Xi = floor ( x );  Yi = floor ( y )
        if Xi==self.Ar[0].Ub : Xi=self.Ar[0].Ub-1     # убирает данное с (не 0) границы.
        if Yi==self.Ar[1].Ub : Yi=self.Ar[1].Ub-1
        dx = x-Xi;  dy = y-Yi
        return (   self.grd[Xi  ,Yi  ] * ( 1- dx ) * ( 1- dy ) 
                 + self.grd[Xi+1,Yi  ] * (    dx ) * ( 1- dy ) 
	         + self.grd[Xi  ,Yi+1] * ( 1- dx ) * (    dy ) 
	         + self.grd[Xi+1,Yi+1] * (    dx ) * (    dy ) )

    def sumXX ( self ) :
        return  sum ( self.neNDT[x-1,y] * self.neNDT[x,y] * self.neNDT[x+1,y] * 
                     ( self.grd[x-1,y]-2*self.grd[x,y]+self.grd[x+1,y] )**2  
                    for y in self.Ar[1].NodS    for x in self.Ar[0].mNodSm )
    def sumYY ( self ) :
        return  sum ( self.neNDT[x,y-1] * self.neNDT[x,y] * self.neNDT[x,y+1] * \
                     ( self.grd[x,y-1]-2*self.grd[x,y]+self.grd[x,y+1] )**2 \
                    for y in self.Ar[1].mNodSm  for x in self.Ar[0].NodS )
    def sumXY ( self ) :
        return  sum ( self.neNDT[x+1,y+1] * self.neNDT[x+1,y-1] * self.neNDT[x-1,y+1] * self.neNDT[x-1,y-1] * 
                     ( self.grd[x+1,y+1]-self.grd[x+1,y-1]-self.grd[x-1,y+1]+self.grd[x-1,y-1] )**2 
                    for y in self.Ar[1].mNodSm  for x in self.Ar[0].mNodSm )

    def F ( self, ArS ) :  # не проверенно
        x = ArS[0]/self.Ar[0].step;  y = ArS[1]/self.Ar[1].step
#        x = ArS[0];   y = ArS[1]
        Xi = floor ( x );  Yi = floor ( y )
        if Xi==self.Ar[0].Ub : Xi=self.Ar[0].Ub-1     # убирает данное с (не 0) границы.
        if Yi==self.Ar[1].Ub : Yi=self.Ar[1].Ub-1     
        return (   self.grd[Xi  ,Yi  ] * ( 1- (x-Xi) ) * ( 1- (y-Yi) ) 
                 + self.grd[Xi+1,Yi  ] * (    (x-Xi) ) * ( 1- (y-Yi) ) 
	         + self.grd[Xi  ,Yi+1] * ( 1- (x-Xi) ) * (    (y-Yi) ) 
	         + self.grd[Xi+1,Yi+1] * (    (x-Xi) ) * (    (y-Yi) ) )
    
    def Freal ( self, ArS_real ) :  
#        return ( self.F( [ (ArS_real[0]-self.Ar[0].min)/self.Ar[0].step,  
#                           (ArS_real[1]-self.Ar[1].min)/self.Ar[1].step ] )
        return ( self.F( [ (ArS_real[0]-self.Ar[0].min),  
                           (ArS_real[1]-self.Ar[1].min) ] )
                 + self.Va.avr
               )

    def SaveSection ( self, fName, sect ) :
        Ax = self.Ar[0]
        Ay = self.Ar[1]
        V = self.Va
        if fName == '' :  fName = V.name + "(" +Ax.name+ ',' +Ay.name+ ")SvF.Sec" 
        fi = open ( fName, "w")
        fi.write ( Ax.name + '\t' + Ay.name + '\t' + V.name + "_SvF\n")       #  загол
        for s in sect :  fi.write ( "\t" + str(s) )     #  точки по х
        for j in Ay.NodS :
            fi.write ( "\n" + str(Ay.min + Ay.step*j) )     #  точки по y
            for s in sect :
                fi.write ( "\t" + str(self.Freal([s, Ay.min + Ay.step*j])() ) )      #  значения
        fi.close()
        print "END of SaveSection"



#    def interPol2a ( self,x,y ) :
 #       Xi = floor ( x );  Yi = floor ( y )
  #      if Xi==self.Ar[0].Ub : Xi=self.Ar[0].Ub-1     # убирает данное с (не 0) границы.
   #     if Yi==self.Ar[1].Ub : Yi=self.Ar[1].Ub-1     
    #    return (   self.grd[Xi  ,Yi  ] * ( 1- (x-Xi) ) * ( 1- (y-Yi) ) 
     #            + self.grd[Xi+1,Yi  ] * (    (x-Xi) ) * ( 1- (y-Yi) ) 
#	         + self.grd[Xi  ,Yi+1] * ( 1- (x-Xi) ) * (    (y-Yi) ) 
#	         + self.grd[Xi+1,Yi+1] * (    (x-Xi) ) * (    (y-Yi) ) )

    def SaveSol ( self, fName ) :
        Ax = self.Ar[0]
        Ay = self.Ar[1]
        V = self.Va
        if fName == '' :  fName = "SvF_"+V.name + "(" +Ax.name+ ',' +Ay.name+ ").sol"
        fi = open ( fName, "w")
        fi.write ( Ax.name + '\t' + Ay.name + '\t' + V.name + "_SvF\n")       #  загол
        for i in Ax.NodS :  fi.write ( "\t" + str(Ax.min + Ax.step*i) )     #  точки по х
        for j in Ay.NodS :
            fi.write ( "\n" + str(Ay.min + Ay.step*j) )     #  точки по y
            for i in Ax.NodS :
                print >> fi, "\t" + "%20.16g" % ((V.avr + self.grd[i,j]())),       #  значения
        fi.close()
        print "END of SaveSol"



    def SaveGrid ( self, TranspGrid, fn ) :
        if TranspGrid == 'N':
            Ax = self.Ar[0]
            Ay = self.Ar[1]
        else :
            Ay = self.Ar[0]
            Ax = self.Ar[1]
        if fn == '' : fn = self.Va.name + "(" +Ax.name+ "," +Ay.name+ ")_SvF.asc"   
        f = open ( fn, "w")
        f.write( "NCOLS "   + str(Ax.Ub+1) )
        f.write( "\nNROWS " + str(Ay.Ub+1) )
        XLLCORNER = Ax.min-Ax.step*.5                   # на край ячейки
        YLLCORNER = Ay.min-Ay.step*.5                   # на край ячейки
        f.write( "\nXLLCORNER " + str(XLLCORNER) )
        f.write( "\nYLLCORNER " + str(YLLCORNER) )
        f.write( "\nCELLSIZE " + str(Ax.step) )            # stepX !
        f.write( "\nNODATA_VALUE " + str(self.NDT) )
        for y in range(Ay.Ub+1) :
          f.write( "\n" )
          for x in range(Ax.Ub+1) :
            if TranspGrid == 'N':
              if not self.neNDT[ x,Ay.Ub-y] :
                 f.write ( " " + str (self.NDT) )
              else :
                if self.type == 'g' :
                  f.write ( " " + str( self.grd[x, Ay.Ub-y]() + self.Va.avr ) )
                else :
                  f.write ( " " + str( self.F([x, Ay.Ub-y])() + self.Va.avr ) )
            else :
              if not self.neNDT[ Ay.Ub-y,x] :
                 f.write ( " " + str (self.NDT) )
              else :
                if self.type == 'g' :
                  f.write ( " " + str( self.grd[Ay.Ub-y,x]() + self.Va.avr ) )
                else :
                  f.write ( " " + str( self.F([Ay.Ub-y,x])() + self.Va.avr ) )
        f.close()
        print "END of SaveGrid"



        
    def ReadSol ( self, ReadFrom ) :
      if ReadFrom == '' :
            ReadFrom = "SvF_"+self.Va.name + "(" +self.Ar[0].name+ ',' +self.Ar[1].name+ ").sol"

      try:
            fi = open ( ReadFrom, "r")
      except IOError as e:
            print "не удалось открыть файл", ReadFrom
            return;
      else:

        print "ReadSol from", ReadFrom,  fi.readline().split(),
        fi.readline().split()
        tb = loadtxt (fi,'double')
        print "shape", tb.shape
#        print self.Ar[1].Ub, self.Ar[0].Ub
        for j in self.Ar[1].NodS :
            for i in self.Ar[0].NodS :
                self.grd[i,j].value = (tb[j*(tb.shape[0]-1)/self.Ar[1].Ub       
                                         ,i*(tb.shape[1]-2)/self.Ar[0].Ub + 1   
                                         ] -self.Va.avr)  #  значения в новых узлах
        fi.close()
        
        
    def SaveDeriv ( self, fName ) :
        Ax = self.Ar[0]
        Ay = self.Ar[1]
        V = self.Va
    # Y
        if fName == '' :  fName = "SvF_"+V.name + "(" +Ax.name+ ',' +Ay.name+ ").Yder"
        fi = open ( fName, "w")
        fi.write ( Ax.name + '\t' + Ay.name + '\t' + V.name + "_Yder\n")       #  загол
        for i in Ax.NodS :  fi.write ( "\t" + str(Ax.min + Ax.step*i) )     #  точки по х
        for j in Ay.mNodSm :
            fi.write ( "\n" + str(Ay.min + Ay.step*j) )     #  точки по y
            for i in Ax.NodS :
                fi.write ( "\t" + str(V.avr + (self.grd[i,j+1]()-self.grd[i,j-1]())
                                              /(2*Ay.step) ) )  #  значения
        fi.close()
    # X
        fName = "SvF_"+V.name + "(" +Ax.name+ ',' +Ay.name+ ").Xder"
        fi = open ( fName, "w")
        fi.write ( Ax.name + '\t' + Ay.name + '\t' + V.name + "_Xder\n")       #  загол
        for i in Ax.mNodSm :  fi.write ( "\t" + str(Ax.min + Ax.step*i) )     #  точки по х
        for j in Ay.NodS :
            fi.write ( "\n" + str(Ay.min + Ay.step*j) )     #  точки по y
            for i in Ax.mNodSm :
                fi.write ( "\t" + str(V.avr + (self.grd[i+1,j]()-self.grd[i-1,j]())
                                              /(2*Ax.step) ) )  #  значения
        fi.close()
        print "END of SaveDeriv"

    def InitByData ( self ) :
        if str(type(self.tbl)) == '<type \'int\'>' : return
        for m in self.sR :
            if self.tbl[m,self.Va.num] == self.NDT : continue
            self.grd[floor(0.499999999+self.tbl[m,self.Ar[0].num]/self.Ar[0].step),
                     floor(0.499999999+self.tbl[m,self.Ar[1].num]/self.Ar[1].step)]   \
            = self.tbl[m,self.Va.num]




# POLY            ********************************************************
class pFun (Fun) :                                
    def __init__ (self, Data, G, grd, Va, ArS, maxP, neNDT, Nxxs ) :
        self.Ini ( Data, 'p', Va, ArS, G, grd, neNDT, Nxxs )
        self.maxP  = maxP
        self.sizeP = PolySize ( self.dim, maxP )
        print "PolySize", self.sizeP
#        self.PolyR = PolyRange ( self.dim, self.maxP )
        self.PolyR = range ( self.sizeP )
        self.pow   = CrePolyPow ( self.dim, self.maxP )
        print self.pow
        self.Dxx, self.Cxx = CreDeriv2Pow ( self.pow, 0, 0 )
        print self.Dxx
        print self.Cxx
        if self.dim > 1 :
            self.Dyy, self.Cyy = CreDeriv2Pow ( self.pow, 1, 1 )
            self.Dxy, self.Cxy = CreDeriv2Pow ( self.pow, 0, 1 )


    def derivXX1 (self, x ) :
        return sum (  self.Cxx[i] * self.grd[i] * x**self.Dxx[i][0]
                        for i in self.PolyR )
    def derivXX (self, x, y ) :
        return sum (  self.Cxx[i] * self.grd[i] * x**self.Dxx[i][0]
                                                * y**self.Dxx[i][1]
                        for i in self.PolyR )
    def derivYY (self, x, y ) :
        return sum (  self.Cyy[i] * self.grd[i] * x**self.Dyy[i][0]
                                                * y**self.Dyy[i][1]
                        for i in self.PolyR )
    def derivXY (self, x, y ) :
        return sum (  self.Cxy[i] * self.grd[i] * x**self.Dxy[i][0]
                                                * y**self.Dxy[i][1]
                        for i in self.PolyR )
    def sumXX ( self ) :
        if self.dim == 1 :
            return  sum (  self.neNDT[x] * 
                          ( self.derivXX1 ( x ) )**2  
                        for x in self.Ar[0].NodS )
        else:
            return  sum (  self.neNDT[x,y] * 
                          ( self.derivXX ( x, y ) )**2  
                    for y in self.Ar[1].NodS    for x in self.Ar[0].NodS )
    def sumYY ( self ) :
        return  sum (  self.neNDT[x,y] * 
                     ( self.derivYY ( x, y ) )**2  
                    for y in self.Ar[1].NodS    for x in self.Ar[0].NodS )
    def sumXY ( self ) :
        return  sum (  self.neNDT[x,y] * 
                     ( self.derivXY ( x, y ) )**2  
                    for y in self.Ar[1].NodS    for x in self.Ar[0].NodS )

    def Ftbl ( self, n ) :
#        x = self.tbl[n,self.Ar[0].num]/self.Ar[0].step;    
        x = self.tbl[n,self.Ar[0].num]
        if self.dim == 1 :
            return sum ( self.grd[i] * x**self.pow[i][0]
                        for i in self.PolyR )
        else :            
            y = self.tbl[n,self.Ar[1].num]/self.Ar[1].step
            return sum ( self.grd[i] * x**self.pow[i][0]
                                 * y**self.pow[i][1]
                        for i in self.PolyR )
        
    def F1 ( self, Ar ) :
            return sum ( self.grd[i] * Ar**self.pow[i][0]
                        for i in self.PolyR )
    def F2 ( self, Ar1, Ar2 ) :
            return sum ( self.grd[i] * Ar1**self.pow[i][0] * Ar2**self.pow[i][1]
                            for i in self.PolyR )
        
    def F ( self, ArS ) :
        if self.dim == 1 :
            return sum ( self.grd[i] * ArS[0]**self.pow[i][0]
                        for i in self.PolyR )
        else :
            return sum ( self.grd[i] * ArS[0]**self.pow[i][0] * ArS[1]**self.pow[i][1]
                            for i in self.PolyR )

    def Freal1 ( self, Ar_real ) :  
            return ( sum ( self.grd[i] * (Ar_real-self.Ar[0].min)**self.pow[i][0]
                        for i in self.PolyR )
                   + self.Va.avr
                   )
        
    def Freal ( self, ArS_real ) :  
        return ( self.F( [ (ArS_real[0]-self.Ar[0].min), (ArS_real[1]-self.Ar[1].min) ] )
                 + self.Va.avr
               )
        
    def SaveSol ( self, fName ) :
        if fName == '' :
            if self.dim == 1 : fName = "SvF_"+self.Va.name + "(" +self.Ar[0].name+ ").pol"
            else :  fName = "SvF_"+self.Va.name + "("+self.Ar[0].name+","+self.Ar[1].name+ ").pol"
        f = open ( fName, "w")
        for i in self.PolyR :
#            f.write ( "\n" + str(self.grd[i]()) + "\t" + str(self.pow[i][0]) )
            print >> f, "\n" + "%20.16g" % (self.grd[i]()) + "\t", str(self.pow[i][0]) 
            if self.dim == 2 :
                f.write ( "\t" + str(self.pow[i][1]) )
        f.close()

        if self.dim == 1 :
            A = self.Ar[0]
            V = self.Va
            fName = "SvF_"+V.name + "(" +A.name+ ").sol"
            fi = open ( fName, "w")
            fi.write ( A.name + '\t' + V.name + "_SvF\n")
            for i in A.NodS :
                fi.write ( "\n"+str(A.min + A.step*i)
                            + "\t"+str(V.avr + self.F1(float(i))()) )
#                            + "\t"+str( (V.avr + self.F1(float(i))()) * (A.min + A.step*i) ) )
            fi.close()
        print "END of SaveSol (Poly)"

    def ReadSol ( self, fName ) :
        if fName == '' :
            if self.dim == 1 : fName = "SvF_"+self.Va.name + "(" +self.Ar[0].name+ ").pol"
            else :  fName = "SvF_"+self.Va.name + "("+self.Ar[0].name+","+self.Ar[1].name+ ").pol"
        fi = open ( fName, "r")
        tb = loadtxt (fi,'double')
        fi.close()
        print "ReadSol from", fName, "shape", tb.shape
        for i in range (min(tb.shape[0], self.sizeP)) :    self.grd[i].value = tb[i,0]

#***********************************************************************            

def CreDeriv1Pow ( polyPow, Cin, xyz ) :
        derPow = copy.deepcopy(polyPow)
        C = copy.deepcopy(Cin)
        if len(C) == 0:   C = [1 for j in range(len(derPow)) ]
        for p in range(len(derPow)) :
            if derPow[p][xyz] == 0 :
                C[p] = 0
            else:
                C[p] *= derPow[p][xyz]
                derPow[p][xyz] -= 1
        return  derPow, C

def CreDeriv2Pow ( polyPow, xyz1, xyz2 ) :
         d1, C = CreDeriv1Pow ( polyPow, [], xyz1 )
         return CreDeriv1Pow ( d1, C, xyz2 )

#def PolyRange ( dim, maxP ) :
def PolySize ( dim, maxP ) :
        size = 0
        for i in range((maxP+1)**dim) :
            sumP = 0
            tmpP = i
#            print "i", i 
            for d1 in range(dim) :
                d = dim-d1-1
                power = int( tmpP/((maxP+1)**d) )
                sumP += power
#                print "d", d, "power", power, "tmpP", tmpP, "sumP", sumP 
                tmpP -= power * ((maxP+1)**d)
#            print "sumP", sumP 
            if sumP <= maxP : size += 1
##        print "PolySize", size
#        return range(size)
        return  size

def CrePolyPow ( dim, maxP ) :
        polyPow = []
        for i in range((maxP+1)**dim) :
            powers = [[0] for j in range(dim) ]
            sumP = 0
            tmpP = i
#            print "i", i, 
            for d1 in range(dim) :
                d = dim-d1-1
                powers[d] = int( tmpP/((maxP+1)**d) )
                sumP += powers[d]
#                print "d", d, "power", power, "tmpP", tmpP, "sumP", sumP 
                tmpP -= powers[d] * ((maxP+1)**d)
#            print "sumP", sumP
#            print powers
            if sumP <= maxP : polyPow.append(powers)  
        return polyPow


#  *************************************************************************

def Var_init_fix (Gr) :
            pass;               Gr.grd0 =  Gr.F[0].grd
            if len(Gr.F) > 1 :  Gr.grd1 =  Gr.F[1].grd
            if len(Gr.F) > 2 :  Gr.grd2 =  Gr.F[2].grd
            if len(Gr.F) > 3 :  Gr.grd3 =  Gr.F[3].grd
            if len(Gr.F) > 4 :  Gr.grd4 =  Gr.F[4].grd
            if len(Gr.F) > 5 :  Gr.grd5 =  Gr.F[5].grd
            if len(Gr.F) > 6 :  Gr.grd6 =  Gr.F[6].grd
            if len(Gr.F) > 7 :  Gr.grd7 =  Gr.F[7].grd
            if len(Gr.F) > 8 :  Gr.grd8 =  Gr.F[8].grd
            Fix        ( Gr.F )   
            InitByData ( Gr.F )

def Fix ( PartS ):
      for p in PartS : p.Fix()

def InitByData ( PartS ):
      for p in PartS :
          if p.type != 'p' :  p.InitByData()


    
def  addQVar ( Data, Gr, Ar1, VarS ):
            tmpV = []
            for v in VarS :
                if v.num >= 0 : tmpV.append (v)
            neNDT, Nxx = Data.neNDT1 ( Ar1, tmpV )   #   только те где есть данные
            for q in range(len(VarS)) :
               Gr.F.append( gFun1 ( Data, Gr, Var ( Ar1.NodS, domain=Reals, initialize = 1 ),
                           VarS[q], Ar1, neNDT , Nxx ) )
def  addGridFunc1D ( Data, Gr, Ar1, V ):
            neNDT, Nxx = Data.neNDT1 ( Ar1, [V] )
            Gr.F.append( gFun1 ( Data, Gr, Var ( Ar1.NodS, domain=Reals, initialize = 1 ),
                           V, Ar1, neNDT , Nxx ) )
            
def  addGridFunc2D ( Data, Gr, Ar1, Ar2, V ):
            neNDT, Nxx, Nyy, Nxy = Data.neNDT2 ( Ar1, Ar2, [V] )
            Gr.F.append( gFun2 ( Data, Gr,
                                 Var ( Ar1.NodS, Ar2.NodS, domain=Reals, initialize = 1 ),
#                       Var ( Ar1.NodS, Ar2.NodS, # bounds=(0.0,10.0)
 #                                                within=NonNegativeReals, initialize = 1 ),
                         V, Ar1, Ar2, neNDT, Nxx, Nyy, Nxy ) )

def  addPolyFunc ( Data, Gr, Ars, V, maxP ):
        poly_dim = len(Ars)
        PolyR = range ( PolySize ( poly_dim, maxP ) )
        if poly_dim == 1 :
            neNDT, Nxx = Data.neNDT1 ( Ars[0], [V] )
#            PolyR = PolyRange ( 1, maxP )
            Gr.F.append( pFun ( Data, Gr, Var ( PolyR, domain=Reals, initialize = 1 ),
                           V, Ars, maxP, neNDT, [Nxx] ) )
        elif poly_dim == 2:
            neNDT, Nxx, Nyy, Nxy = Data.neNDT2 ( Ars[0], Ars[1], [V] )
#            PolyR = PolyRange ( 2, maxP )
            Gr.F.append( pFun ( Data, Gr, Var ( PolyR, domain=Reals, initialize = 1 ),
                           V, Ars, maxP, neNDT, [Nxx, Nyy, Nxy] ) )
        else :
            print "********* Not ready **************"

def ParsFuncSimple ( Data, func ) :        #   T(Ro,Time)   
        s =func.replace(' ','').split('(')
        Va = Data.Va(s[0])
#        print Va.name
        s = s[1].split(')')
        s = s[0].split(',')
        Ars = []
        for a in range(len(s)) :
            Ars.append (Data.Ar(s[a]))
#            print Ars[-1].name
        return Va, Ars


def  addGFunc ( Gr, Data, func ) : # "T(Ro,Time)"
        Va, Ars = ParsFuncSimple ( Data, func )
        if len(Ars) == 1 :  addGridFunc1D ( Data, Gr, Ars[0], Va )
        else :              addGridFunc2D ( Data, Gr, Ars[0], Ars[1], Va )

def  addPFunc ( Gr, Data, func, maxP ) : 
        Va, Ars = ParsFuncSimple ( Data, func )
        addPolyFunc ( Data, Gr, Ars, Va, maxP )

      



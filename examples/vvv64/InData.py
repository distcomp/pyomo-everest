# -*- coding: utf-8 -*-
from  numpy import *
# from pyomo.environ import *

#from GlobName import * 


class Vari :                  #  var
  def __init__ (self, name) : 
      self.name = name
      self.num  = -99
      self.NoR  = 0
      self.avr  = 0
      self.sigma  = 1
  def Vprint(self) :
      print "Var", self.name, self.num, "NoR", self.NoR, "avr", self.avr, "sig", self.sigma

class Arg :                 #  Arg
  def __init__ (self, name) : 
      self.name = name
      self.num  = -99
      self.min  = -1e34
      self.max  = +1e34
      self.step = -34
      self.vis  = 0
      self.Ub   = 0         # сетка от 0 до Ub
      self.NodS = 0
      self.mNodSm = 0
      self.mNodS = 0
  def Aprint(self) :
      print "Arg", self.name, self.num, "mm", self.min, self.max, "st", self.step, "vis", self.vis 

class Cond :                 #  Cond
  def __init__ ( self, name, rel, Nval ) :     #  Имя, Условие, Число, Номер колонки имени
      self.name = name
      self.rel  = rel
      self.Nval = Nval
      self.num  = -99
  def Cprint(self) :  print self.name, self.rel, self.Nval, self.num 
 
class Col :                 #  допол колонки 
  def __init__ ( self, name ) :     #  Имя, Номер колонки имени
      self.name = name
      self.num  = -99
  def Coprint(self) :  print self.name, self.num 


class InData :
  def __init__ ( self ) :
    
    self.V = [ ]             #  var
    self.A = [ ]             #  Arg
    self.C = [ ]             # Cond
    self.Col = []
    self.NDT   = -99999
    self.tbl   = 0
    self.NoR   = 0
    self.sR    = []
    self.cols  = []

  def Va (self, name) :
      for v in range(len(self.V)) :
          if self.V[v].name == name : return self.V[v]
      return 0    

  def Ar (self, name) :
      for a in range(len(self.A)) :
          if self.A[a].name == name : return self.A[a]
      return 0    
  
  def ReadTbl ( self, InFile, DataPath ):
    if DataPath != '' : InFile = DataPath + '/' + InFile
    print "InFile: ", InFile    
    fi = open (InFile)
    self.cols = fi.readline().split()
    print "cols: ", self.cols

    self.tbl = loadtxt (fi,'double')
#    self.tbl [:,0] += 100     #  SRTM для Линника
#    self.tbl [:,1] += 50     
    fi.close()
    print "end of ReadTbl  tbl.shape ", self.tbl.shape


  def CheckNames ( self ):

    for d in range(len(self.V)) :
      if self.cols.count(self.V[d].name)>0 :
        self.V[d].num = self.cols.index(self.V[d].name)
      else :
        print "************************************ No NUM For ", self.V[d].name
      print "Var", d,  ;  self.V[d].Vprint()

    for d in range( len(self.A) ) :
        if self.cols.count(self.A[d].name)>0:
            self.A[d].num = self.cols.index(self.A[d].name)
        else :
            if d==0 :  print "*************** Err No name for X *********************"
            else :
                print "******************  Dim = 1   *********************"
                self.dim = 1
        print "Arg", d,  ;  self.A[d].Aprint()

    for c in range(len(self.C)) :
        if self.cols.count(self.C[c].name)>0:
            self.C[c].num = self.cols.index(self.C[c].name)
        else :
            print "*************** Err No name for Cond ***************", self.C[c].Cprint()
        print "Cond", c,  ; self.C[c].Cprint()  

    for c in range(len(self.Col)) :
        if self.cols.count(self.Col[c].name)>0:
            self.Col[c].num = self.cols.index(self.Col[c].name)
        else :
            print "*************** Err No name for Col ***************", self.Col[c].Cprint()
        print "Col", c, ; print self.Col[c].name, self.Col[c].num  
#        print "Col", c, ; self.Col[c].Coprint()  

    

  def ClareTbl( self ):
    self.NoR = 0
    if str(type(self.tbl)) == '<type \'int\'>' : return
    for i in range(self.tbl.shape[0]) :

##        if self.tbl[i,12] != self.NDT : self.tbl[i,12] = 1.2 * self.tbl[i,12]

        OK = 0
        for d in range(len(self.V)) :    #  если хоть один живой
            if self.V[d].num != -99 :
                if self.tbl[i,self.V[d].num] != self.NDT : OK = 1; break
        if not OK : continue

#        for name in range(self.dim) :
        for name in range(len(self.A)) :
            if self.A[name].num < 0 : continue
            if self.tbl[i,self.A[name].num] == self.NDT : OK = 0; break
            if self.tbl[i,self.A[name].num] < self.A[name].min : OK = 0; break 
            if self.tbl[i,self.A[name].num] > self.A[name].max : OK = 0; break
        if not OK : continue

        for c in range(len(self.C)) :
            if self.tbl[i,self.C[c].num] == self.NDT : OK = 0; break
            if self.C[c].rel == "<"  and not self.tbl[i,self.C[c].num] <  self.C[c].Nval : OK = 0; break 
            if self.C[c].rel == ">"  and not self.tbl[i,self.C[c].num] >  self.C[c].Nval : OK = 0; break 
            if self.C[c].rel == "<=" and not self.tbl[i,self.C[c].num] <= self.C[c].Nval : OK = 0; break 
            if self.C[c].rel == ">=" and not self.tbl[i,self.C[c].num] >= self.C[c].Nval : OK = 0; break 
            if self.C[c].rel == "==" and not self.tbl[i,self.C[c].num] == self.C[c].Nval : OK = 0; break 
            if self.C[c].rel == "!=" and not self.tbl[i,self.C[c].num] != self.C[c].Nval : OK = 0; break 
        if not OK : continue

        self.tbl[self.NoR] = self.tbl[i]
        self.NoR += 1
    self.sR = range (self.NoR)    
    print "NoR", self.NoR
    print "mins", self.tbl.min(0)
    print "maxs", self.tbl.max(0)
    
    print "End ClareTbl"        
    self.tbl = delete (self.tbl, range(self.NoR,self.tbl.shape[0]),0)


  def WriteTbl ( self, OutFile ):
    fi = open (OutFile, "w")
    for ar in self.A :
        print >> fi, ar.name, "\t", 
    for va in self.V :
        print >> fi, va.name, "\t", 
    for co in self.Col :
        print >> fi,  "\t"+ co.name,
    print >> fi, ''
    for i in range(self.tbl.shape[0]) :
        for ar in self.A :
            print >> fi, self.tbl[i,ar.num], '\t',
        for va in self.V :
            print >> fi, self.tbl[i,va.num], '\t',
        for co in self.Col :
            print >> fi, self.tbl[i,co.num], '\t',
        print >> fi, ''
    fi.close()


  def ReadGrid_VS( self, ReadFrom, DataPath, ReadDirection ) :
        if DataPath != '' : ReadFrom = DataPath + '/' + ReadFrom
        fi = open ( ReadFrom, "r")
        self.cols = fi.readline().split()
        print "cols: ", self.cols
        cols = fi.readline().split()
        x = zeros( len(cols), float64 )
        for j in range(len(x)) : x[j] = float(cols[j])
        tb = loadtxt (fi,'double')
        fi.close()
        print "Grid_VS", tb.shape
        self.tbl = zeros( ( len(x)*tb.shape[0],3 ), float64 )
        m = 0
        if 'X' == ReadDirection :
            for i in range(tb.shape[0]) : 
                for j in range(len(x)) :
                  self.tbl[m,0] = x[j]
                  self.tbl[m,1] = tb[i,0]
                  self.tbl[m,2] = tb[i,j+1]
                  m += 1
        else :  
            for j in range(len(x)) :
                for i in range(tb.shape[0]) : 
                  self.tbl[m,0] = x[j]
                  self.tbl[m,1] = tb[i,0]
                  self.tbl[m,2] = tb[i,j+1]
                  m += 1
#        if len(self.A)<1 :  self.A.append ( Arg('X') )
 #       if len(self.A)<2 :  self.A.append ( Arg('Y') )
  #      self.A[0].num = 0 
   #     self.A[1].num = 1 
    #    self.V[0].num = 2
     #   self.dim  = 2
        print "tbl.shape ", self.tbl.shape


  def ReadGrid( self, ReadGridFrom, DataPath ) :
        if DataPath != '' : ReadGridFrom = DataPath + '/' + ReadGridFrom
        fi = open ( ReadGridFrom, "r")
        grdX      = int(fi.readline().split()[1])
        grdY      = int(fi.readline().split()[1])
        XLLCORNER = float(fi.readline().split()[1])
        YLLCORNER = float(fi.readline().split()[1])
        CELLSIZE  = float(fi.readline().split()[1])
        self.NDT  = float(fi.readline().split()[1])
        print grdX, grdY, XLLCORNER, YLLCORNER, CELLSIZE, self.NDT
        gr = loadtxt (fi,'double')
        print gr.shape
        fi.close()

        self.tbl = zeros( (grdX*grdY,3), float64 )
        YSIZE = (grdY-1)*CELLSIZE; 
        XLLCORNER += CELLSIZE*.5                            # на центр ячейки
        YLLCORNER += CELLSIZE*.5
        ma = 0;
        for y in range(grdY) :
          for x in range(grdX) :
            if gr[y,x] != self.NDT :
                    self.tbl[ma,0] = x * CELLSIZE + XLLCORNER
                    self.tbl[ma,1] = YSIZE - y * CELLSIZE +YLLCORNER
#                    self.tbl[ma,2] = gr[y,x] * 37
                    self.tbl[ma,2] = gr[y,x] 
                    ma += 1
        print "NoR", ma
        self.tbl = delete (self.tbl, range(ma,self.tbl.shape[0]),0)
        if len(self.A)<1 :  self.A.append ( Arg('X') )
        if len(self.A)<2 :  self.A.append ( Arg('Y') )
        self.A[0].num = 0 
        self.A[1].num = 1 
        self.V[0].num = 2
        self.dim  = 2



  def ToGrid ( self, OutFile, Gr ):
    A0 = self.A[0]
    A1 = self.A[1]
    f = open ( OutFile, "w")
    print  "Write to ", OutFile
    f.write( "NCOLS "   + str(A0.Ub+1) )
    f.write( "\nNROWS " + str(A1.Ub+1) )
    XLLCORNER = A0.min-A0.step*.5                   # на край ячейки
    YLLCORNER = A1.min-A1.step*.5                   # на край ячейки
    f.write( "\nXLLCORNER " + str(XLLCORNER) )
    f.write( "\nYLLCORNER " + str(YLLCORNER) )
    f.write( "\nCELLSIZE " + str(A0.step) )            # stepX !
    f.write( "\nNODATA_VALUE " + str(self.NDT) )
    for y in range(A1.Ub+1) :
         f.write( "\n" )
         for x in range(A0.Ub+1) :
             if Gr.grd1[ x,A1.Ub-y] == self.NDT :
                 f.write ( " " + str (self.NDT) )
             else :
                 #if MODE == ("N") then
                 f.write ( " " + str( Gr.grd1[x, A1.Ub-y]() + self.V[0].avr ) )
#                 f.write ( " 0" )
                 #if MODE == ("P") then  printf: " %f", (sum { px in s0pX, py in s0pY} c[px,py] * (x)^px * (grdY-y)^py) + V[0].avr > (OutFile); 
    f.close()
    print "END of write into   ", OutFile



  def SaveSol_D1 ( self, OutFile, Gr ):

    fi = open ( OutFile, "w" )
    fi.write ( self.A[0].name )
    for v in range(len(self.V)) :
#        if self.V[v].num != -99 :
          fi.write ( "\t" + self.V[v].name + "_SvF")
    for i in self.A[0].NodS :
        fi.write (   "\n" + str(self.A[0].min+self.A[0].step*i) 
                   + "\t" + str(Gr.grd1 [i]()*self.V[0].sig + self.V[0].avr) )
#                   + "\t" + str(Gr.grd [i]()) )
        if len(self.V) > 1 :
          fi.write ( "\t" + str(Gr.grd2[i]() + self.V[1].avr) )
#          fi.write ( "\t" + str(Gr.grd1[i]()) )
        if len(self.V) > 2 :
          fi.write (   "\t" + str(Gr.grd3[i]() + self.V[2].avr) )
                 
    fi.close()



        
  def SavePoints_D1 ( self, OutFile, Gr ):
    fi = open ( OutFile, "w" )
    fi.write ( self.A[0].name + "  " + self.V[0].name + "  " + self.V[0].name + "_SvFs\n" )
    for n in self.A[0].NodS :
        fi.write (   str(Gr.X[n]*self.A[0].step+self.A[0].min) + "  "
                   + str(Gr.F[n]+self.V[0].avr) + "  "
                   + str((Gr.F[n]-delta1(Gr,n)())+self.V[0].avr ) + "\n" )
    fi.close()

  def SaveCols(self) : 
        fi = open ( "SvF_"+self.A[0].name+"_Cols.txt", "w" )
        fi.write ( self.A[0].name )
        for c in range(len(self.Col)) :
            fi.write ( "\t" + self.Col[c].name)
        for n in range (self.NoR) :
            fi.write (   "\n" + str( self.A[0].min + self.A[0].step*self.tbl[n,self.A[0].num] ) )
            for c in range(len(self.Col)) :
                fi.write ( "\t" + str( self.tbl[n,self.Col[c].num] ) )
        fi.close()
        print "Save Cols"






  def SigEst ( self, maxSigEst ) :
    sig2  = 0
    Nsig2 = 0
    for r in range(1,self.NoR) :
        if abs(self.tbl[r-1,self.A[0].num]-self.tbl[r,self.A[0].num]) <= maxSigEst :
                sig2  += ( 1/2.*self.tbl[r,self.V[0].num]-1/2.*self.tbl[r-1,self.V[0].num] )**2
                Nsig2 +=1
    sigSS2 = sqrt( 2 * sig2/Nsig2 )
    print "Nsig2 = ", Nsig2, "     sigSS2 = ", sigSS2 
    sig3  = 0
    Nsig3 = 0
    for r in range(1,self.NoR-1) :
        if (    abs(self.tbl[r-1,self.A[0].num]-self.tbl[r,self.A[0].num]) <= maxSigEst
            and abs(self.tbl[r,self.A[0].num]-self.tbl[r+1,self.A[0].num]) <= maxSigEst ) :
                sig3  += (2/3.*self.tbl[r,self.V[0].num]-1/3.*self.tbl[r-1,self.V[0].num]-1/3.*self.tbl[r+1,self.V[0].num])**2
                Nsig3 +=1
    sigSS3 = sqrt( 3/2.* sig3/Nsig3 )
    print "Nsig3 = ", Nsig3, "     sigSS3 = ", sigSS3 
    sig5  = 0
    Nsig5 = 0
    for r in range(2,self.NoR-2) :
        if (    abs(self.tbl[r-2,self.A[0].num]-self.tbl[r-1,self.A[0].num]) <= maxSigEst
            and abs(self.tbl[r-1,self.A[0].num]-self.tbl[r  ,self.A[0].num]) <= maxSigEst 
            and abs(self.tbl[r  ,self.A[0].num]-self.tbl[r+1,self.A[0].num]) <= maxSigEst 
            and abs(self.tbl[r+1,self.A[0].num]-self.tbl[r+2,self.A[0].num]) <= maxSigEst ) :
                sig5  += ( 4/5.*self.tbl[r,self.V[0].num]
                          -1/5.*self.tbl[r-2,self.V[0].num]-1/5.*self.tbl[r-1,self.V[0].num]
                          -1/5.*self.tbl[r+1,self.V[0].num]-1/5.*self.tbl[r+2,self.V[0].num])**2
                Nsig5 +=1
    sigSS5 = sqrt( 5/4.* sig3/Nsig5 )
    print "Nsig5 = ", Nsig5, "     sigSS5 = ", sigSS5 


  def Normalization ( self, VarNormalization ) :
    for d in range(len(self.A)) :
        if self.A[d].min == -1e34 : self.A[d].min = self.tbl.min(0)[self.A[d].num] 
        if self.A[d].max ==  1e34 : self.A[d].max = self.tbl.max(0)[self.A[d].num]
        if self.A[d].step < 0 : self.A[d].step = - (self.A[d].max-self.A[d].min) / self.A[d].step;
        if self.A[d].vis  < 0 : self.A[d].vis  = - self.A[d].vis * self.A[d].step;
        self.A[d].Aprint()    
#        print "Limmits "+self.A[d].name+":", self.A[d].min, self.A[d].max    

        if self.A[d].num >= 0 :
            self.tbl [:,self.A[d].num] -= self.A[d].min     # not приводим к штукам шагов
#            self.tbl [:,self.A[d].num] /= self.A[d].step
        self.A[d].vis /= self.A[d].step
    
#    print self.tbl.min(0)
#    print self.tbl.max(0)

    for d in range(len(self.V)) :
        if self.V[d].num == -99 :  continue
        self.V[d].NoR = sum ( self.tbl[m,self.V[d].num]!=self.NDT for m in range(self.NoR) )  # NoR
        self.V[d].avr = 1./self.V[d].NoR * \
            sum ( (self.tbl[m,self.V[d].num]!=self.NDT) * self.tbl[m,self.V[d].num] for m in range(self.NoR) )  # среднее
        self.V[d].sigma = sqrt ( 1./(self.V[d].NoR-1) * \
            sum ( (self.tbl[m,self.V[d].num]!=self.NDT) * (self.tbl[m,self.V[d].num]-self.V[d].avr)**2 for m in range(self.NoR)))  # дисп
        self.V[d].Vprint()

        if 'Y' == VarNormalization :
          for m in range(self.NoR) :
            if self.tbl[m,self.V[d].num]!=self.NDT:  self.tbl[m,self.V[d].num] -= self.V[d].avr
#          for m in range(self.NoR) :
#            if self.tbl[m,self.V[d].num]!=self.NDT:  self.tbl[m,self.V[d].num] /= self.V[d].sig
        else :
            self.V[d].avr = 0
#            self.V[d].sig = 1
#    self.V[d].Vprint()    


  def makeNodes ( self, n ) :    # n  -номер координаты
      print 's', self.A[n].step
      Xi = array ( floor( self.tbl[:,self.A[n].num] ),"int")
      grdX = int (ceil ( max (  self.tbl.max(0)[self.A[n].num],
                               (self.A[n].max-self.A[n].min)/self.A[n].step ) ) )
      for i in range(len(Xi)) :
          if Xi[i]==grdX : Xi[i]=grdX-1     # убирает данное с (не 0) границы.
      return Xi, grdX                       # вычисляем по внутренней четверке узлов


  def grdUbSets ( self, Arg ) :    # n  -номер координаты
      Arg.Ub = int ( ceil ( (Arg.max-Arg.min)/Arg.step ) )
      if Arg.num >= 0 :
          Arg.Ub = int (ceil ( max ( self.tbl.max(0)[Arg.num]/Arg.step, Arg.Ub )))
      Arg.NodS   = range (0, Arg.Ub+1)
      Arg.mNodSm = range (1, Arg.Ub  )
      Arg.mNodS  = range (1, Arg.Ub+1)
#      print "Ub for Arg"+str(Arg.num),   Arg.Ub
    

  def neNDT1 ( self, Ar1, VaS ) :   # если хоть один из  VaS != NDT, то узел активен
      visA = Ar1.vis
      numA = Ar1.num
      self.grdUbSets ( Ar1 )

      neNDT = zeros ( Ar1.Ub+1,int8 )

      if visA==0 :
        for x in range( Ar1.Ub+1 ) :  neNDT[x] = 1
      else:
        for v in range(len(VaS)) :
          if VaS[v].num == -99 :  continue
          for m in range(self.NoR) :
              if self.tbl[m,VaS[v].num]!=self.NDT :
                  neNDT[floor(0.499999999+self.tbl[m,Ar1.num]/Ar1.step)] = 1 
        for m in range(self.NoR) :
          for x in range( max(0,           int(floor((self.tbl[m,numA]-visA)/Ar1.step))), 
                          min(Ar1.Ub,int(ceil ((self.tbl[m,numA]+visA)/Ar1.step)))+1 ) :
               neNDT[x] = 1
               
      Nxx = sum ( neNDT[x-1]*neNDT[x]*neNDT[x+1] for x in range( 1,Ar1.Ub ) )
#      print "Nxx.. ", Nxx
      return neNDT, Nxx


#  NOT TESTED YET    
  def   neNDT2 (self, Ar1, Ar2, VaS ) :   # если хоть один из  VaS != NDT, то узел активен
      self.grdUbSets ( Ar1 )
      self.grdUbSets ( Ar2 )

      neNDT = zeros ( (Ar1.Ub+1, Ar2.Ub+1), int8 )

      if Ar1.vis==0 and Ar2.vis==0  :
        for x in range( Ar1.Ub+1 ) :  
          for y in range( Ar2.Ub+1 ) :  neNDT[x,y] = 1
      else :
#        for m in range(self.NoR) :
#              if self.tbl[m,self.V[0].num]!=self.NDT :
#                  neNDT[int(self.tbl[m,Ar1.num]),int(self.tbl[m,Ar2.num])] = 1 

        for v in range(len(VaS)) :
          if VaS[v].num == -99 :  continue
          for m in range(self.NoR) :
#              if self.tbl[m,VaS[v].num]!=self.NDT :
#                  neNDT[int(self.tbl[m,Ar1.num]),int(self.tbl[m,Ar2.num])] = 1 
              if self.tbl[m,VaS[v].num]!=self.NDT :
                  neNDT[floor(0.499999999+self.tbl[m,Ar1.num]/Ar1.step),
                        floor(0.499999999+self.tbl[m,Ar2.num]/Ar2.step)] = 1 

        for m in range(self.NoR) :
          for x in range( max(0,     int(floor((self.tbl[m,Ar1.num]-Ar1.vis)/Ar1.step))), 
                          min(Ar1.Ub,int(ceil ((self.tbl[m,Ar1.num]+Ar1.vis)/Ar1.step)))+1 ) :
            for y in range( max(0,     int(floor((self.tbl[m,Ar2.num]-Ar2.vis)/Ar2.step))), 
                            min(Ar2.Ub,int(ceil ((self.tbl[m,Ar2.num]+Ar2.vis)/Ar2.step)))+1 ) :
               neNDT[x,y] = 1

      Nxx = sum ( neNDT[x-1,y] * neNDT[x,y] * neNDT[x+1,y]  \
                    for y in Ar2.NodS    for x in Ar1.mNodSm )
      Nyy = sum ( neNDT[x,y-1] * neNDT[x,y] * neNDT[x,y+1]  \
                    for y in Ar2.mNodSm  for x in Ar1.NodS )
      Nxy = sum ( neNDT[x+1,y+1] * neNDT[x+1,y-1] * neNDT[x-1,y+1] * neNDT[x-1,y-1]
                    for y in Ar2.mNodSm  for x in Ar1.mNodSm )
#      print "Nxx.. ", Nxx, Nyy, Nxy
      return neNDT, Nxx, Nyy, Nxy


      

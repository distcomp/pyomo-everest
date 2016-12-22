# -*- coding: cp1251 -*-
from __future__ import division
from  numpy import *
from pyomo.environ import *

from Lego import *


def calcNvz (Gr) :
              h_r = Gr.F[0].Ar[0].step
              h_t = Gr.F[0].Ar[1].step
              for r in Gr.F[3].Ar[0].mNodSm :
#                print r
                for t in Gr.F[3].Ar[1].mNodSm :
                    Gr.grd3[r,t] =   \
                       ( 3*(Gr.grd0[r,t+1]-Gr.grd0[r,t-1])/(2*h_t) 
                       - ( 1./(r*h_r)*(Gr.grd0[r+1,t]-Gr.grd0[r-1,t])/(2*h_r)
                         + (Gr.grd0[r+1,t]-2*Gr.grd0[r,t]+Gr.grd0[r-1,t])/h_r**2 
                         - 1./(r*h_r)*(Gr.grd1[r+1]  -Gr.grd1[r-1]  )/(2*h_r)
                         - (Gr.grd1[r+1]  -2*Gr.grd1[r]  +Gr.grd1[r-1]  )/h_r**2
                         ) * Gr.Hrel * 1e4 / 58**2 
                       ) ()
def calcPi (Gr) :
              h_r = Gr.F[0].Ar[0].step
              h_t = Gr.F[0].Ar[1].step
              for r in Gr.F[3].Ar[0].mNodSm :
                for t in Gr.F[3].Ar[1].mNodSm :
                    Gr.grd3[r,t] =   \
                       ( 3*(Gr.grd0[r,t+1]-Gr.grd0[r,t-1])/(2*h_t) 
                       ) ()
              for r in Gr.F[3].Ar[0].NodS :
                    Gr.grd3[r,0] = 0;
                    Gr.grd3[r,Gr.F[0].Ar[1].Ub] = 0;
              for t in Gr.F[3].Ar[1].mNodSm :
                    Gr.grd3[0,t] = 0;
                    Gr.grd3[Gr.F[0].Ar[0].Ub, t] = 0;
def calcDif (Gr) :
              h_r = Gr.F[0].Ar[0].step
              h_t = Gr.F[0].Ar[1].step
              for r in Gr.F[3].Ar[0].mNodSm :
                for t in Gr.F[3].Ar[1].mNodSm :
                    Gr.grd3[r,t] =   \
                       ( 
                         ( 1./(r*h_r)*(Gr.grd0[r+1,t]-Gr.grd0[r-1,t])/(2*h_r)
                         + (Gr.grd0[r+1,t]-2*Gr.grd0[r,t]+Gr.grd0[r-1,t])/h_r**2 
                         - 1./(r*h_r)*(Gr.grd1[r+1]  -Gr.grd1[r-1]  )/(2*h_r)
                         - (Gr.grd1[r+1]  -2*Gr.grd1[r]  +Gr.grd1[r-1]  )/h_r**2
                         ) * Gr.Hrel * 1e4 / 58**2 
                       ) ()
              for r in Gr.F[3].Ar[0].NodS :
                    Gr.grd3[r,0] = 0;
                    Gr.grd3[r,Gr.F[0].Ar[1].Ub] = 0;
              for t in Gr.F[3].Ar[1].mNodSm :
                    Gr.grd3[0,t] = 0;
                    Gr.grd3[Gr.F[0].Ar[0].Ub, t] = 0;





def createGr ( Datas, Penal ) :
            Gr = ConcreteModel()
            Gr.mu  = Param (Datas[0].sR, mutable=True, initialize = 1 )   ##  int???
            Gr.F = []

            addGFunc ( Gr, Datas[0], 'T(Ro,Time)'    )          # T(Ro,Time)  grd0
            addGFunc ( Gr, Datas[1], 'T0(Ro)'        )          # T0(Ro)      grd1
            addGFunc ( Gr, Datas[2], 'E0(Ro)'        )          # E0(Ro)      grd2
            addGFunc ( Gr, Datas[3], 'Nvs(Ro,Time)'  )          # Nvs(Ro,Time)grd3
            addPFunc ( Gr, Datas[4], 'K(T)', Datas[4].PolyPow ) # K(T)        grd4
            addGFunc ( Gr, Datas[5], 'E(Ro,Time)'    )          # E(Ro,Time)       grd5

            Var_init_fix (Gr)
            Gr.Hrel = Var ( domain=Reals, bounds=(0.1,10.0), initialize = 0.100002061569 ) #5.48415125193 )#0.993920482491 )#1. ) #9.99998077649 ) #9.38728024854 ) #10.0 )
#            Gr.Hrel.fixed = True

#            def Teq0(Gr, t) :  return ( Gr.grd0[Gr.F[0].Ar[0].Ub,t] == 0 )     # border T = 0
#            Gr.Teq0 = Constraint( Gr.F[0].Ar[1].NodS, rule=Teq0 )

            h_r = Gr.F[0].Ar[0].step
            h_t = Gr.F[0].Ar[1].step
            rITB = int ( 0.3 / h_r )

            S_0_1    = range ( 0,    Gr.F[0].Ar[0].Ub+1 )
            S_0_rITB = range ( 0,    rITB )
            S_rITB_1 = range ( rITB, Gr.F[0].Ar[0].Ub+1 )
            
            def K(T) :
                return Gr.F[4].Freal1(T)
            def Q(T) :
                return T * Gr.F[4].Freal1(T)


            def Neviyska(Gr,r,t) :
                return ( Gr.grd3[r,t] ==
                         3*(Gr.grd0[r,t+1]-Gr.grd0[r,t-1])/(2*h_t) 
                       - ( 1./(r*h_r)*(Gr.grd0[r+1,t]-Gr.grd0[r-1,t])/(2*h_r)
                         + (Gr.grd0[r+1,t]-2*Gr.grd0[r,t]+Gr.grd0[r-1,t])/h_r**2 
                         - 1./(r*h_r)*(Gr.grd1[r+1]  -Gr.grd1[r-1]  )/(2*h_r)
                         - (Gr.grd1[r+1]  -2*Gr.grd1[r]  +Gr.grd1[r-1]  )/h_r**2
                         ) * Gr.Hrel * 1e4 / 58**2 
                       ) 
#            Gr.eqNeviyska = Constraint( Gr.F[3].Ar[0].NodS, Gr.F[3].Ar[1].mNodSm, rule=Neviyska )
            Gr.eqNeviyska = Constraint( Gr.F[3].Ar[0].mNodSm, Gr.F[3].Ar[1].mNodSm, rule=Neviyska )



            def obj_expression(G):
                return (
#    + Gr.F[0].Complexity ( [Penal[0], Penal[1]] ) + Gr.F[3].Complexity ( [Penal[2], Penal[3]] )
     + Gr.F[0].Complexity ( [Penal[2], Penal[3]] ) + Gr.F[3].Complexity ( [Penal[0], Penal[1]] )
                            + Gr.F[0].MSD( ) 
                        )
            Gr.OBJ = Objective(rule=obj_expression)

#            Gr.F[0].SaveGrid ( 'Y' )

            Gr.F[1].FixAll()
            Gr.F[2].FixAll()
            Gr.F[4].FixAll()
            Gr.F[5].FixAll()

#            Gr.F[0].SaveSol('')
#            a=1/0

            Gr.F[0].ReadSol ( '' )

            Gr.F[3].ReadSol ( '' )
            if 1==1 :
                calcNvz (Gr)

            print_resB(Gr, Penal)
           
            return Gr

def print_resB(Gr, Penal):
#            OB = Gr.OBJ()
            print    Penal
            print    "OBJ ", Gr.OBJ()
            print    "T -C", Gr.F[0].Complexity ( [Penal[2], Penal[3]] )()
            print    "T -M", Gr.F[0].MSDno_mu( )()
            print    "Nv-C", Gr.F[3].Complexity ( [Penal[0], Penal[1]] )()
#            print    "K -C", Gr.F[4].Complexity ( [Penal[2]] )()
#            print    "T0-M", Gr.F[1].MSDno_mu( )()
#            print    "E0-M", Gr.F[2].MSDno_mu( )() 
#           print    "E()-M", Gr.F[5].MSDno_mu( )()
            print    "Hrel", Gr.Hrel()

def print_res(Gr, Penal):
            print_resB(Gr, Penal)

            calcPi (Gr);        Gr.F[3].SaveGrid ( 'Y', 'Pi.asc' )
            calcDif (Gr);       Gr.F[3].SaveGrid ( 'Y', 'Dif.asc' )
            
            return

            h_r = Gr.F[0].Ar[0].step
            h_t = Gr.F[0].Ar[1].step

            rITB = int ( 0.3 / h_r )

            S_0_1    = range ( 0,    Gr.F[0].Ar[0].Ub+1 )
            S_0_rITB = range ( 0,    rITB )
            S_rITB_1 = range ( rITB, Gr.F[0].Ar[0].Ub+1 )
            def K(T) :
                return Gr.F[4].Freal1(T)
            def Q(T) :
                return T * Gr.F[4].Freal1(T)

            print "t0",
            print sum( Gr.grd2[r1] * Q(Gr.grd1[r1]) * r1 for r1 in S_0_1   )()
            for r1 in S_0_1 :
                print r1, Gr.grd2[r1].value,  Q(Gr.grd1[r1])(), Gr.grd1[r1].value

#            a=1/0  


            for t in Gr.F[3].Ar[1].mNodSm :
                print t, 
                print sum( Gr.grd2[r1] * Q(Gr.grd0[r1,t]) * r1 for r1 in S_0_1   )(),
                print sum( Gr.grd2[r1] * K(Gr.grd0[r1,t]) * r1 for r1 in S_0_1   )(),
                print sum( Gr.grd2[r1] * Q(Gr.grd0[r1,t]) * r1 for r1 in S_0_rITB)(),
                print sum( Gr.grd2[r1] * K(Gr.grd0[r1,t]) * r1 for r1 in S_0_rITB)(),
                print sum( Gr.grd2[r1] * Q(Gr.grd0[r1,t]) * r1 for r1 in S_rITB_1)(),
                print sum( Gr.grd2[r1] * K(Gr.grd0[r1,t]) * r1 for r1 in S_rITB_1)()
                
            print "t0",
            print sum( Gr.grd2[r1] * Q(Gr.grd1[r1]) * r1 for r1 in S_0_1   )(),
            print sum( Gr.grd2[r1] * K(Gr.grd1[r1]) * r1 for r1 in S_0_1   )(),
            print sum( Gr.grd2[r1] * Q(Gr.grd1[r1]) * r1 for r1 in S_0_rITB)(),
            print sum( Gr.grd2[r1] * K(Gr.grd1[r1]) * r1 for r1 in S_0_rITB)(),
            print sum( Gr.grd2[r1] * Q(Gr.grd1[r1]) * r1 for r1 in S_rITB_1)(),
            print sum( Gr.grd2[r1] * K(Gr.grd1[r1]) * r1 for r1 in S_rITB_1)(),

#            a=1/0


#


            for r in Gr.F[3].Ar[0].mNodSm :
                for t in Gr.F[3].Ar[1].mNodSm :
                   Gr.grd3[r,t] =   \
                         3*((Gr.grd0[r,t+1]-Gr.grd0[r,t-1])/(2*h_t))() 
            Gr.F[3].SaveSol('pi.sol')

            for r in Gr.F[3].Ar[0].mNodSm :
                for t in Gr.F[3].Ar[1].mNodSm :
                   Gr.grd3[r,t] =   \
                       ( ( r < rITB ) *
                         (  K(Gr.grd0[r,t])()
                            * (        sum( Gr.grd5[r1,t] * Q(Gr.grd0[r1,t]) * r1 for r1 in S_0_1   )
                              + Gr.E * sum( Gr.grd5[r1,t] * Q(Gr.grd0[r1,t]) * r1 for r1 in S_0_rITB)
                                     * sum( Gr.grd5[r1,t] * K(Gr.grd0[r1,t]) * r1 for r1 in S_rITB_1)
                                     * h_r 
                              ) 
                            / (        sum( Gr.grd5[r1,t] * K(Gr.grd0[r1,t]) * r1 for r1 in S_0_1   )
                              + Gr.E * sum( Gr.grd5[r1,t] * K(Gr.grd0[r1,t]) * r1 for r1 in S_0_rITB)
                                     * sum( Gr.grd5[r1,t] * K(Gr.grd0[r1,t]) * r1 for r1 in S_rITB_1)
                                     * h_r 
                              )
                          - K(Gr.grd1[r])
                            * (        sum( Gr.grd2[r1] * Q(Gr.grd1[r1]) * r1 for r1 in S_0_1   )
                              + Gr.E * sum( Gr.grd2[r1] * Q(Gr.grd1[r1]) * r1 for r1 in S_0_rITB)
                                     * sum( Gr.grd2[r1] * K(Gr.grd1[r1]) * r1 for r1 in S_rITB_1)
                                     * h_r 
                              ) 
                            / (        sum( Gr.grd2[r1] * K(Gr.grd1[r1]) * r1 for r1 in S_0_1   )
                              + Gr.E * sum( Gr.grd2[r1] * K(Gr.grd1[r1]) * r1 for r1 in S_0_rITB)
                                     * sum( Gr.grd2[r1] * K(Gr.grd1[r1]) * r1 for r1 in S_rITB_1)
                                     * h_r 
                              )
                         )()
                        +( r >= rITB ) *
                         (  K(Gr.grd0[r,t])()
                            * (        sum( Gr.grd5[r1,t] * Q(Gr.grd0[r1,t]) * r1 for r1 in S_0_1   )
                              + Gr.E * sum( Gr.grd5[r1,t] * K(Gr.grd0[r1,t]) * r1 for r1 in S_0_rITB)
                                     * sum( Gr.grd5[r1,t] * Q(Gr.grd0[r1,t]) * r1 for r1 in S_rITB_1)
                                     * h_r 
                              ) 
                            / (        sum( Gr.grd5[r1,t] * K(Gr.grd0[r1,t]) * r1 for r1 in S_0_1   )
                              + Gr.E * sum( Gr.grd5[r1,t] * K(Gr.grd0[r1,t]) * r1 for r1 in S_0_rITB)
                                     * sum( Gr.grd5[r1,t] * K(Gr.grd0[r1,t]) * r1 for r1 in S_rITB_1)
                                     * h_r 
                              )
                          - K(Gr.grd1[r])
                            * (        sum( Gr.grd2[r1] * Q(Gr.grd1[r1]) * r1 for r1 in S_0_1   )
                              + Gr.E * sum( Gr.grd2[r1] * K(Gr.grd1[r1]) * r1 for r1 in S_0_rITB)
                                     * sum( Gr.grd2[r1] * Q(Gr.grd1[r1]) * r1 for r1 in S_rITB_1)
                                     * h_r 
                              ) 
                            / (        sum( Gr.grd2[r1] * K(Gr.grd1[r1]) * r1 for r1 in S_0_1   )
                              + Gr.E * sum( Gr.grd2[r1] * K(Gr.grd1[r1]) * r1 for r1 in S_0_rITB)
                                     * sum( Gr.grd2[r1] * K(Gr.grd1[r1]) * r1 for r1 in S_rITB_1)
                                     * h_r 
                              )
                         )()
                       )
            Gr.F[3].SaveSol('scob.sol')
                   
            for r in Gr.F[3].Ar[0].mNodSm :
                for t in Gr.F[3].Ar[1].mNodSm :
                   Gr.grd3[r,t] =   \
                       ( ( 1./(r*h_r)*(Gr.grd0[r+1,t]-Gr.grd0[r-1,t])/(2*h_r)
                         + (Gr.grd0[r+1,t]-2*Gr.grd0[r,t]+Gr.grd0[r-1,t])/h_r**2 
                         - 1./(r*h_r)*(Gr.grd1[r+1]  -Gr.grd1[r-1]  )/(2*h_r)
                         - (Gr.grd1[r+1]  -2*Gr.grd1[r]  +Gr.grd1[r-1]  )/h_r**2
                         ) * Gr.Hrel * 1e4 / 58**2 
                       ) ()
                    

            Gr.F[3].SaveSol('dif.sol')
            
            a=1/0

            

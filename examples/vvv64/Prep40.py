# -*- coding: utf-8 -*-
from  numpy import *


#def makeNodes ( tbl, numAn, maxAn, minAn, stepAn ) :
 #   Xi = array ( floor( tbl[:,numAn] ),"int")
  #  print  "LLLLL", tbl.max(0)[numAn], (maxAn-minAn)/stepAn 
   # grdX = int (ceil ( max ( tbl.max(0)[numAn], (maxAn-minAn)/stepAn ) ) )
    #for i in range(len(Xi)) :
     #   if Xi[i]==grdX : Xi[i]=grdX-1     # убирает данное с (не 0) границы.
#    return Xi, grdX                       # вычисляем по внутренней четверке узлов


#from pyomo.environ import *


def PrepReg1tmp ( G, visA, NDT, X, F ):
        for  m in G.sR :  G.grd[int(X[m])].value = F[m]  
        if visA==0 :
            memF = 0.0;             # может надо поискать ближайшую ?
            for x in G.sX :
                if G.grd[x].value==NDT : G.grd[x].value = memF
                else :                   memF = G.grd[x]
        else :
            for  m in G.sR :
                for x in range( max(0,     int(floor(X[m]-visA))), 
                                min(G.grdX,int(ceil (X[m]+visA)))+1 ) :
                    if G.grd[x].value==NDT : G.grd[x].value = F[m]
            for x in G.sX : 
                if G.grd[x].value == NDT :  G.grd[x].fixed = True
        return;
    
def PrepReg1 ( G, visA, NDT ):
        for  m in G.sR :  G.grd[int(G.X[m])].value = G.F[m]  
        if visA[0]==0 :
            memF = 0.0;             # может надо поискать ближайшую ?
            for x in G.sX :
                if G.grd[x].value==NDT : G.grd[x].value = memF
                else :                   memF = G.grd[x]
        else :
            for  m in G.sR :
                for x in range( max(0,     int(floor(G.X[m]-visA[0]))), 
                                min(G.grdX,int(ceil (G.X[m]+visA[0])))+1 ) :
                    if G.grd[x].value==NDT : G.grd[x].value = G.F[m]
            for x in G.sX : 
                if G.grd[x].value == NDT :  G.grd[x].fixed = True
        return;

def PrepReg2 ( G, visA, NDT ):
        for  m in G.sR :  G.grd[int(G.X[m]),int(G.Y[m])].value = G.F[m]
###        return
#        for x in G.sX : 
 #             for y in G.sY :
  #                  if G.grd[x,y].value ==NDT :
   #                     print "NDT", x, y, NDT, G.grd[x,y].value
        if visA[0]==0 and visA[1]==0:
            memF = 0.0;             # может надо поискать ближайшую ?
            for x in G.sX :
              for y in G.sY :
                if G.grd[x,y].value==NDT : G.grd[x,y].value = memF  # заполняем оставшиеся
                else :                     memF = G.grd[x,y].value
        else :
            for  m in G.sR :
              for x  in  range( max(0,     int(floor(G.X[m]-visA[0]))), 
                                min(G.grdX,int(ceil (G.X[m]+visA[0])))+1 ) :
                for y in range( max(0,     int(floor(G.Y[m]-visA[1]))), 
                                min(G.grdY,int(ceil (G.Y[m]+visA[1])))+1 ) :
                    if G.grd[x,y].value ==NDT :
#                        print "NDT", x, y, NDT, G.grd[x,y].value
                        G.grd[x,y].value = G.F[m]
#                        print G.grd[x,y].value
            for x in G.sX : 
              for y in G.sY :
                if G.grd[x,y].value == NDT :  G.grd[x,y].fixed = True
        return;




def Prep1 ( G ):
    Nxx = sum ( G.eqNDT[x-1] * G.eqNDT[x] * G.eqNDT[x+1]  for x in G.sXm )
    print "Nxx.. ", Nxx
    return Nxx


def Prep ( G ):
    Nxx = sum ( G.eqNDT[x-1,y] * G.eqNDT[x,y] * G.eqNDT[x+1,y]  \
                    for y in G.sY   for x in G.sXm )
    Nyy = sum ( G.eqNDT[x,y-1] * G.eqNDT[x,y] * G.eqNDT[x,y+1]  \
                    for y in G.sYm  for x in G.sX )
    Nxy = sum ( G.eqNDT[x+1,y+1] * G.eqNDT[x+1,y-1] * G.eqNDT[x-1,y+1] * G.eqNDT[x-1,y-1]
                    for y in G.sYm  for x in G.sXm )
    print "Nxx.. ", Nxx, Nyy, Nxy
    return Nxx, Nyy, Nxy


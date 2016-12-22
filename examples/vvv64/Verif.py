from  numpy import *


def makeStepSets ( NoR, CVstep ):
    if CVstep > 0  :  CVSetSize   = int ( ceil( NoR / CVstep ) )
    else :
        CVSetSize = - CVstep 
        CVstep = int ( ceil( NoR / CVSetSize ) )
    print "CVstep", CVstep, "CVSetSize", CVSetSize
    vSet = []
    for p in range(CVstep) :
        vSet.append ([])
#        print "NN", p, "\n"
        for i in range(p, NoR, CVstep) :
            vSet[p].append (i)
#            print i,
        
    mSet = vSet       
    return vSet, mSet

def makePartSets ( NoR, CVpartSize, CVside ) :
    if CVpartSize < 0 :  CVpartSize   = int ( ceil( NoR / (-CVpartSize) ) )
    if CVside     < 0 :  CVside       = int ( ceil( CVpartSize * (-CVside) ) )

    vSet = []
    mSet = []
    for p in range(0, NoR, CVpartSize) :
        vSet.append ([])
        for i in range( p,               min(p+CVpartSize,NoR) ) :        vSet[-1].append (i)
        mSet.append ([])
        for i in range( max(0,p-CVside), min(p+CVpartSize+CVside,NoR) ) : mSet[-1].append (i)
    print "CVpartSize", CVpartSize, "CVside", CVside, "len(vSet)", len(vSet)
    return vSet, mSet

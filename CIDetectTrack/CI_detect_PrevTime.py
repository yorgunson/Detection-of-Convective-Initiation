import sys
sys.path.append('/mnt/user/soner.yorgun/utils')
from datetime import datetime, timedelta
import numpy as np
import scipy as sp
import scipy.spatial
from collections import OrderedDict
import math
import multiprocessing
from multiprocessing import Lock,Queue

import db_utils_CI
from prod_proj import ProdProj as pp

###################################
# Construct Classes and Functions #
###################################

# Function to find the minimum edge-to-edge distance between objects
def get_minEdgeDist(ref,it):
    
    mytree=sp.spatial.cKDTree(ref)
    dist,indices= mytree.query(it)
    mindist=np.min(dist)
    minidx=np.argmin(dist)
    idx=indices[minidx]

    return mindist,ref[idx],it[minidx]

# Function to find the minimum cmass-to-cmass distance between objects
def get_minCmassDist(ref,it):
	
	mincmass=()
	mindist=100000

	for i in range(len(it)):
		euc_dist=((ref[0]-it[i][0])**2+(ref[1]-it[i][1])**2)**0.5

		if euc_dist<mindist:
			mindist=euc_dist
			mincmass=(it[i][0],it[i][1])
				
	return mindist,mincmass

def great_circle(ref,minmatch,pp_src):

    y1=ref[0];x1=ref[1]
    y2=minmatch[0];x2=minmatch[1]
    
    lat1, lon1 = pp.map_xy(pp_src,x1,y1,mkInt='round')
    lat2, lon2 = pp.map_xy(pp_src,x2,y2,mkInt='round') 

    PI = 4.0 * math.atan2(1,1)
    DEGREES_TO_RADIANS = PI / 180.0
    EARTH_RADIUS = 6371.229

    Lat1 = float(lat1) * DEGREES_TO_RADIANS
    Lon1 = float(lon1) * DEGREES_TO_RADIANS
    Lat2 = float(lat2) * DEGREES_TO_RADIANS
    Lon2 = float(lon2) * DEGREES_TO_RADIANS

    p1 = math.cos(Lat1) * math.cos(Lon1) * math.cos(Lat2) * math.cos(Lon2)
    p2 = math.cos(Lat1) * math.sin(Lon1) * math.cos(Lat2) * math.sin(Lon2)
    p3 = math.sin(Lat1) * math.sin(Lat2)
    coeff=p1+p2+p3

    if coeff>1.0 or coeff<-1.0:
        d=0
    else:
        d =  math.acos(coeff) * EARTH_RADIUS
    
    return d

# Function to compute the Minimum Great Circle Distancebetween objects (previous time-step)
def GetPrevGCD(config,time,issue,lead,level,th,ref,bounds,prev_objij,field,pp_src,refgrids,out_q):
    
    prev_edgedist,prev_ref_idx,prev_it_idx=get_minEdgeDist(refgrids,prev_objij)
            
    prevmin_gcd=great_circle(prev_ref_idx,prev_it_idx,pp_src)
    
    if prevmin_gcd>config.prev_th: b=1
    else: b=0
    
    out_q.put((b,time,issue,lead,level,th,ref,bounds,field))

#############
# DETECT CI #
#############
def detectCI(src,db,config,time,issue,lead,level,th,bounds,pp_src,field):
    
    print 'Detecting CI...'
    
    ##################################################################
    # Checking the object sizes and their proximity to other objects #
    ##################################################################
    out_q = Queue()
    small_obj=db_utils_CI.get_AllObjCmass_Area(db,config.obj_table,src,time,issue,lead,level,th,bounds,config.size_th,'<=')
       
    ######################################################
    # Checking the previous time step to identify the CI #
    ######################################################
    
    # Read all the object ijs from the previous time step
    prevtime=time-timedelta(minutes=config.timestep)
    
    # Change the lead to the previous timestep if it is a forecast
    
    if src=='HRRR':prevlead=lead-config.timestep
    if src=='CIWS':prevlead=lead
    
    # Get the number of objects in the previous time step
    objcount=db_utils_CI.get_ObjCount(db,config.obj_table,src,prevtime,issue,prevlead,level,th,bounds)

    if objcount>0:

        # For each object in the previous time step, check if the edge-to-edge distance threshold is violated
        prev_objij=db_utils_CI.get_AllObjij(db,config.obj_table,src,prevtime,issue,prevlead,level,th,bounds)  
        
        detect_args=[]
        
        for ref in small_obj:
            
            refgrids=db_utils_CI.get_SingleObjij_Cmass(db,config.obj_table,src,time,issue,lead,level,th,ref,bounds)
            
            detect_args.append([config,time,issue,lead,level,th,ref,bounds,prev_objij,field,pp_src,refgrids,out_q])       

        
        procs=[multiprocessing.Process(target=GetPrevGCD, args=(detect_args[i])) for i in range(len(detect_args))]
        
        for p in procs:
            p.start()
            
        res=[]
        for i in range(len(procs)):
            res.append(out_q.get())
            
        for p in procs:p.join()
        
        # Update the CI candidate field for the objects that pass the threshold check
        for re in res:
            if re[0]==1:
                db_utils_CI.write_CI_Cmass(db,config.obj_table,src,re[1],re[2],re[3],re[4],re[5],re[6],re[7],re[8])        
    return


if "__main__" == __name__:
    
    src='CIWS'
    config= __import__('config_CI_'+src)
    db=db_utils_CI.get_conn(config.hostname, config.username, config.password, config.database)
    
    years=[2015]
    months=[5]#[4]
    days=[5]#[1]
    hours=[0]
    minutes=[0,5,10,15,20,25,30,35,40,45,50,55]
    
    src='CIWS'
    issue=999
    lead=999
    th=3.5
    
    # CIWS Area Bound
    ################################
    bounded=True
    lat1=38.2;lat2=39.6
    lon1=-98.3;lon2=-97

    if bounded==False:
        bounds='{999}'
        dims=[999]
            
    elif bounded==True:
                        
        x1, y1 = pp.map_latlon(pp.ciws(),lat1,lon1,mkInt='round')
        x2, y2 = pp.map_latlon(pp.ciws(),lat2,lon2,mkInt='round')        
        bounds='{{'+str(x1)+','+str(y1)+'},{'+str(x2)+','+str(y2)+'}}'
        
    for year in years:
        for month in months:
            for day in days:
                for hour in hours:
                    for minute in minutes:
                        
                        dt=OrderedDict([('year',year),('month',month),('day',day),('hour',hour),('minute',minute)])
                        time=datetime(year,month,day,hour,minute)
                        
                        print time
                        
                        cl=detectCI(src,db,config,time,issue,lead,0,th,bounds)
                        print 'Found',len(cl),'CI candidates'

from __future__ import division
import sys
sys.path.append('/mnt/user/soner.yorgun/utils')
from netCDF4 import Dataset
from time import strftime, strptime
from datetime import datetime, timedelta
import numpy as np
import math
from prod_proj import ProdProj as pp
import numpy.ma as ma
import scipy as sp
import scipy.spatial
import multiprocessing
from multiprocessing import Lock,Queue


import db_utils_CI as dbutils

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

# Function to find the movement quadrant
def quadrant(p1, p2):
	pp1=(0,0)
	pp2=(p2[1]-p1[1],p2[0]-p1[0])

	ang1 = np.arctan2(*pp1)
	ang2 = np.arctan2(*pp2)
	quad_ang=np.rad2deg((ang2 - ang1) % (2 * np.pi))
	
	if quad_ang>=0 and quad_ang<90:quad=1
	if quad_ang>=90 and quad_ang<180:quad=2    
	if quad_ang>=180 and quad_ang<270:quad=3
	if quad_ang>=270 and quad_ang<360:quad=4
	
	return quad_ang,quad

def SAL_Filter(refgrids,refarea,iterobjs,db,config,out_q):
    
    sal_obj=[]

    for iterobj in iterobjs:

        itercmass=(iterobj[1],iterobj[2])
        
        itergrids=dbutils.get_SingleObjij_id(db,config.obj_table,iterobj[5])

        ee_dist,ref_idx,it_idx=get_minEdgeDist(refgrids,itergrids)
        
        area_diff=abs(refarea-iterobj[3])*config.area_coeff

        q=0.3*area_diff+0.7*ee_dist
        
        if q<=config.Q: sal_obj.append((tuple(iterobj)))
                
    out_q.put((sal_obj))



#########################################################
########## TRACKING CI FORWARD IN TIME  #################
#########################################################

def trackCI_HRRR(src,db,config,dtime,issue,lead,level,th,bounds,endtimestep,cifield,evolfield,trackfield):
    
    #print '***********************'
    #print 'Tracking CI forward in time'
    
    ci,ci_id=dbutils.get_allhrrrCI(db,config.obj_table,src,dtime,issue,lead,th,bounds,cifield)
    
    for i in range(len(ci)):
        #print 'CI+ID:',ci_id[i]
        #print '*************'
        
        ci_evol_list=[]
        
        refcmass=ci[i][0]
        refvalid=dtime
        reflead=lead
        refissue=issue
        
        ci_evol_list.append([refvalid,refcmass])
        		
        # Form the time iteration list
        validlist=[refvalid+timedelta(minutes=k*config.timestep) for k in range(1,endtimestep)]
        leadlist=[reflead+k*config.timestep for k in range(1,endtimestep)]
        
        # Reflist / IntermList Elements = 0:datetime, 1:cmass0, 2:cmass1, 3:obj_area, 5:obj_max
        ref_list=[]
        ref_list.append((refvalid,refcmass[0],refcmass[1],ci[i][1],ci[i][2]))
        
        for v in range(len(validlist)):
            
            iterlead=leadlist[v]
            itervalid=validlist[v]
            
            interm_list=[]
            
            for refobj in ref_list:
                
                refcmass=(refobj[1],refobj[2])
                #print 'Refcmass:',refcmass,time
                
                # Get all the objects in the next time step THAT SATIFIES AN AREA within the Minimum Bounding Square (MBS)
                iterobjs=dbutils.get_allObj_MBS_hrrr(db,config.obj_table,src,itervalid,issue,iterlead,th,bounds,refcmass,config.MBS_HalfSide)

                if len(iterobjs)>0:
                    
                    ################################
                    # Calculate SAl, Filter objects
                    ###############################
                    reftime=itervalid-timedelta(minutes=config.timestep)
                    refld=iterlead-config.timestep
                    refarea=refobj[3]
                    refgrids=dbutils.get_SingleObjij_Cmass(db,config.obj_table,src,reftime,issue,refld,level,th,refcmass,bounds)
                    
                    # MultiProcessing
                    out_q=Queue()
                    procs=[multiprocessing.Process(target=SAL_Filter, args=(refgrids,refarea,iterobjs,db,config,out_q))]
                    for p in procs:p.start()

                    sal_objs=[]
                    for k in range(len(procs)):
                        sal_objs.append(out_q.get())
                    
                    for p in procs:p.join()
                        
                    if len(sal_objs[0])>0: 
                        for salobj in sal_objs[0]:
                            if tuple(salobj) not in interm_list:
                                interm_list.append(tuple(salobj))
                    ########################
                    
            ref_list=interm_list
            
            for evol in interm_list:
                ci_evol_list.append([evol[0],(evol[1],evol[2])])
        
        #################################
        # Write the ci_evol to database #
        #################################
        
        if src=='CIWS':
            issue=999;lead=999;level=0
        
        checklist=[]
        for k in range(len(ci_evol_list)):
            if (ci_evol_list[k][0],ci_evol_list[k][1][0],ci_evol_list[k][1][1]) not in checklist:
                dbutils.write_CIevol_Cmass(db,config.obj_table,src,ci_evol_list[k][0],issue,iterlead,level,th,ci_evol_list[k][1],bounds,evolfield,trackfield,ci_id[i])
                				
                checklist.append((ci_evol_list[k][0],ci_evol_list[k][1][0],ci_evol_list[k][1][1]))
        
if "__main__" == __name__:

	src='CIWS'
	config= __import__('config_CI_'+src)
	db=dbutils.get_conn(config.hostname, config.username, config.password, config.database)
	
	years=[2015]
	months=[5]#[4]
	days=[5]#[1]
	hours=[0]#,1,2,3,4,5,6]#[0,1,2,3,4,5,6]
	minutes=[0,5,10,15,20,25,30,35,40,45,50,55]
	
	src='CIWS'
	issue=999
	lead=999
	th=1
		
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
	
	e=trackCI_Obs(src,db,config,th,bounds,150)
	
	print len(e)
	
	for i in range(len(e)):
		print '**************************'
		for z in e[i]:
			print z
	

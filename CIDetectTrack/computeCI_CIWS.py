import sys
sys.path.append('/mnt/user/soner.yorgun/utils')
from datetime import datetime, timedelta
import numpy as np
from collections import OrderedDict
import multiprocessing
from multiprocessing import Lock

import db_utils_CI
import ObjDetectAtt_v2_db as ODA
import CI_detect_PrevTime as CI_detect
import CI_track_MtoM_ciws as CI_track
from prod_proj import ProdProj as pp

# Full Time Period
years=[2016]
months=[7]
days=[4,5,6,7,8,9,10,11]
hours=range(0,24)
minutes=range(0,60,15)

src='CIWS'
config= __import__('config_CI_'+src)
db=db_utils_CI.get_conn(config.hostname, config.username, config.password, config.database)

th=1

# Area Bound
################################
bounded='yes'

#lat1=34;lat2=47;lon1=-90;lon2=-66 # NE Region Bounds
lat1=30;lat2=36;lon1=-90;lon2=-75 # SE Region Bounds

if bounded=='no':
    bounds=[999]
    dims=[999]
    info=''
    bounds_str='{999}'
        
elif bounded=='yes':
        
    x1, y1 = pp.map_latlon(pp.ciws(),lat1,lon1,mkInt='round')
    x2, y2 = pp.map_latlon(pp.ciws(),lat2,lon2,mkInt='round')        
    bounds=[(x1,y1),(x2,y2)]
    bounds_str='{{'+str(x1)+','+str(y1)+'},{'+str(x2)+','+str(y2)+'}}'
    dims=(str(y2-y1+2),str(x2-x1+2))    
    #info='lat '+str(lat1)+'-'+str(lat2)+', lon '+str(lon1)+'-'+str(lon2)
    info='SE'

    
def detect(src,dt,valid,issue,lead,bounds,dims,th,info):

    try:
        inst=ODA.ObjDetectAtt(src,dt,issue,lead,bounds,dims)
        objects,obj_ij=inst.RegGrow(th)
        attrib=inst.Attrb(config,objects)
        inst.db_write(src,valid,issue,lead,0,th,obj_ij,attrib,bounds,info)
    except:
        print 'File might be missing: ', config.DataFile(dt)
        

def CIdetect(arg_list,lock):
    
    lock.acquire()
    CI_detect2.detectCI(arg_list[0],db,config,arg_list[1],arg_list[2],arg_list[3],arg_list[4],arg_list[5],arg_list[6],arg_list[7],arg_list[8])
    lock.release()
        
detect_args=[];detect_ci_args=[]      
for year in years:
    for month in months:
        for day in days:
            for hour in hours:
                for minute in minutes:
                    
                    dt=OrderedDict([('year',year),('month',month),('day',day),('hour',hour),('minute',minute)])
                    time=datetime(year,month,day,hour,minute)
                    valid=time
                    issue=999
                    lead=999
                    
                    print time, src
                    
                   
                    ### (1) Object Detection [Arguments to feed into the multiprocessing scheme at the end of the code]
                    ###     Run this line first (comment out the next two) to do the initial object extraction from the field
                    ###     This populates the database with the attributes of each object. Once this is run, it should be commented out when next two are running
                    
                    detect_args.append([src,dt,valid,issue,lead,bounds,dims,th,info])
                    
                    ### (2) CI Detection
                    ###     Detects the CI candidates using previous time-step proximity threshold
                    ###     The last argument of the below function has to be changed to specify which column to populate
                    ###     e.g., 'ci_15_6' : ci candidates for 15-minute CIWS using 6km proximity threshold
                    
                    #cl=CI_detect.detectCI(src,db,config,time,issue,lead,0,th,bounds_str,pp.ciws(),'ci_15_6')
                    
                    ### (3) CI Tracing
                    ###     Tracks the CI candidates using the Q parameter
                    ###     The last three arguments of the below function has to be changed to specify which columns to populate
                    ###     e.g., 'ci_15_6' : from the previous step (defines which type of CI candidates to track)
                    ###     e.g., 'ci_evol_15_6q30': the binary column to populate for plotting purposes (Q=30, can be variable)
                    ###     e.g., 'ci_track_15_6q30': the array column to populate for keeping track of object continuations (Q=30, can be variable)
                    
                    #e=CI_track.trackCI_Obs(src,db,config,time,issue,lead,0,th,bounds_str,10,'ci_15_6','ci_evol_15_6q30','ci_track_15_6q30')


### Multiprocessing for Object Detection for step (1)

pool = multiprocessing.Pool(processes=10)
procs = [pool.apply_async(detect, args=(detect_args[i])) for i in range(len(detect_args))]
results = [p.get() for p in procs]


from __future__ import division
import sys
sys.path.append('/mnt/user/soner.yorgun/utils')
sys.path.append('/mnt/user/soner.yorgun/CI/CI_2017/CIDetectTrack')
from netCDF4 import Dataset
from time import strftime, strptime
from datetime import datetime, timedelta
import numpy as np
import math
import numpy.ma as ma
import scipy as sp
import scipy.spatial
import matplotlib
import matplotlib.pyplot as plt

from prod_proj import ProdProj as pp
import db_utils_CI

#src='CIWS'
src='HRRR'
config= __import__('config_CI_'+src)
db=db_utils_CI.get_conn(config.hostname, config.username, config.password, config.database)

th=1

# Area Bound
################################
bounded=True
lat1=34;lat2=47;lon1=-90;lon2=-66 # NE Region Bounds
#lat1=30;lat2=36;lon1=-90;lon2=-75 # SE Region Bounds

if bounded==False:
    bounds=[999]
    dims=[999]
    info=''
    bounds_str='{999}'
        
elif bounded==True:
    
    if src=='CIWS':pp_src=pp.ciws()
    if src=='HRRR':pp_src=pp.hrrr()
    
    x1, y1 = pp.map_latlon(pp_src,lat1,lon1,mkInt='round')
    x2, y2 = pp.map_latlon(pp_src,lat2,lon2,mkInt='round')        
    bounds=[(x1,y1),(x2,y2)]
    bounds_str='{{'+str(x1)+','+str(y1)+'},{'+str(x2)+','+str(y2)+'}}'
    dims=(str(y2-y1+2),str(x2-x1+2))    
    info='lat '+str(lat1)+'-'+str(lat2)+', lon '+str(lon1)+'-'+str(lon2)

    

field='ci_15_18';field_track='ci_track_15_18q1'
table='object_repo_ne_hrrr_q30'
#field='ci';field_track='ci_track'
#table='object_repo_ne_s'


qry1="SELECT id,obj_max FROM "+table+" WHERE src='"+src+"' and th="+str(th)+" and "+field+"=1 and bounds='"+bounds_str+"';"
    
q1=db.query(qry1)
ci=q1.getresult()
tot=0

for i in range(len(ci)):
    
    #print ci[i][0]
    #qry2="SELECT obj_max FROM "+table+" WHERE '"+str(ci[i][0])+"' = ANY("+field_track+") order by obj_max desc limit 1;"
    qry2="SELECT obj_max FROM "+table+" WHERE "+field_track+" @>  ARRAY["+str(ci[i][0])+"] order by obj_max desc limit 1;"
    q2=db.query(qry2)
    ci_max=q2.getresult()
    print i,len(ci_max)
    
    if len(ci_max) > 0:
        if ci_max[0][0]>=3.5 or ci[i][1]>=3.5:
            tot+=1
    else:
        if ci[i][1]>=3.5:
            tot+=1
        
print 'field=',field_track,'CI_cand=',len(ci),'#VIP3=',tot,'%VIP3=',(tot/len(ci))*100



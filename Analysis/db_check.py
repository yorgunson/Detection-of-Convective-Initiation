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
from pg import DB
from collections import OrderedDict

from prod_proj import ProdProj as pp
import db_utils_CI

src='CIWS'
#src='HRRR'
config= __import__('config_CI_'+src)

hostname='fvs-anb2'
database='object_soner'
username='nevsoper'
password=''

db = DB(dbname=database, host=hostname, user=username, passwd=password)

th=1
table='object_repo_regions'

# Area Bound
################################
bounded='yes'
#lat1=38.2;lat2=39.6;lon1=-98.3;lon2=-97
#lat1=30;lat2=40;lon1=-105;lon2=-95
#lat1=30;lat2=36;lon1=-105;lon2=-99
#lat1=30;lat2=33;lon1=-105;lon2=-102.5
lat1=34;lat2=47;lon1=-90;lon2=-66 # NE Region Bounds

if bounded=='no':
    bounds=[999]
    dims=[999]
    info=''
    bounds_str='{999}'
        
elif bounded=='yes':
    
    if src=='CIWS':pp_src=pp.ciws()
    if src=='HRRR':pp_src=pp.hrrr()
    
    x1, y1 = pp.map_latlon(pp_src,lat1,lon1,mkInt='round')
    x2, y2 = pp.map_latlon(pp_src,lat2,lon2,mkInt='round')        
    bounds=[(x1,y1),(x2,y2)]
    bounds_str='{{'+str(x1)+','+str(y1)+'},{'+str(x2)+','+str(y2)+'}}'
    dims=(str(y2-y1+2),str(x2-x1+2))    
    #info='lat '+str(lat1)+'-'+str(lat2)+', lon '+str(lon1)+'-'+str(lon2)
    info='NE'

def get_ObjCount(db,table,src,dtime,issue,lead,level,th,bounds):
    
    qry="SELECT distinct obj_num FROM "+table+" WHERE datetime='"+str(dtime)+"' and src='"+src+"' and issue="+str(issue)+" and lead="+str(lead)+\
        " and level="+str(level)+" and th="+str(th)+" and bounds='"+str(bounds)+"';"
    
    q=db.query(qry)
    objnums=q.getresult()

    if len(objnums)==0:maxobj=0
    else:maxobj=max(objnums)[0]
    
    return maxobj


# Read Object count for each timestep
'''
years=[2016]
months=[7]
days=[4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19]
hours=range(0,24)
minutes=range(0,60,5)

tot=0
times=[];objnums=[]
for year in years:
    for month in months:
        for day in days:
            for hour in hours:
                for minute in minutes:
                    
                    if src=='CIWS':
                        dt=OrderedDict([('year',year),('month',month),('day',day),('hour',hour),('minute',minute)])
                        valid=dt
                        issue=999
                        lead=999
                    if src=='HRRR':
                        ld=str(hour).zfill(2)+str(minute).zfill(2)
                        dt=OrderedDict([('year',year),('month',month),('day',day),('issue',hours[0]),('lead',ld)])
                        valid=OrderedDict([('year',year),('month',month),('day',day),('issue',hour),('lead',minute)])
                        issue=int(hours[0])
                        lead=int(ld)
                        
                    time=datetime(year,month,day,hour,minute)
                    
                    objs=get_ObjCount(db,table,src,time,issue,lead,0,th,bounds_str)
                    tot+=objs
                    print time, objs
                    times.append(time)
                    objnums.append(objs)

print 'Total objs', tot

np.save('times_regions_CIWS',np.array(times))
np.save('objcount_regions_CIWS',np.array(objnums))
'''

# Get all CIWS object attributes
qry="SELECT obj_area,obj_max FROM "+table+" WHERE src='"+src+"' and th="+str(th)+" and bounds='"+str(bounds_str)+"';"

q=db.query(qry)
objatt=q.getresult()

print objatt[0]
np.save('objatt_NE_CIWS',np.array(objatt))



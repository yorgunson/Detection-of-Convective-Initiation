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
from collections import OrderedDict
import matplotlib as mpl
mpl.use('Qt4agg')

from prod_proj import ProdProj as pp
import db_utils_CI

#src='CIWS'
src='HRRR'
config= __import__('config_CI_'+src)
db=db_utils_CI.get_conn(config.hostname, config.username, config.password, config.database)

# Area Bound
################################
bounded=True
#lat1=34;lat2=47;lon1=-90;lon2=-66 # NE Region Bounds
lat1=30;lat2=36;lon1=-90;lon2=-75 # SE Region Bounds

if bounded==False:
    bounds=[999]
    dims=[999]
    info=''
    bounds_str='{999}'
        

##############################################################
#############
### HRRR ####
#############

x1, y1 = pp.map_latlon(pp.hrrr(),lat1,lon1,mkInt='round')
x2, y2 = pp.map_latlon(pp.hrrr(),lat2,lon2,mkInt='round')        
bounds=[(x1,y1),(x2,y2)]
bounds_str='{{'+str(x1)+','+str(y1)+'},{'+str(x2)+','+str(y2)+'}}'
dims=(str(y2-y1+2),str(x2-x1+2))    
info='lat '+str(lat1)+'-'+str(lat2)+', lon '+str(lon1)+'-'+str(lon2)

years=[2016]
months=[7]
days=[4,5,6,7,8,9,10,11]
issues=range(0,24)
leads=range(120,180,15)

# Change Table and Field names for specific application
table_hrrr='object_repo_se_HRRR'
th=1
field='ci_15_18'

obj_max=[];obj_mean=[];obj_area=[];obj_count_hrrr=[]
valid_hrrr=[]
for year in years:
    for month in months:
        for day in days:
            for issue in issues:
                for ld in leads:
                    
                    hr=int(math.floor(ld/60))
                    mnt=ld%60
                    
                    time=datetime(year,month,day)
                    valid=time+timedelta(hours=issue)+timedelta(hours=hr)+timedelta(minutes=mnt)
                    lead=ld
                    
                    print valid, issue, lead
                    valid_hrrr.append(valid)
                    
                    # ONLY FOR CI CANDIDATES
                    qry1="SELECT id,obj_mean,obj_max,obj_area FROM "+table_hrrr+" WHERE datetime='"+str(valid)+"' and issue="+str(issue)+" and lead="+str(lead)+\
                       " and src='HRRR' and th="+str(th)+" and "+field+"=1 and bounds='"+bounds_str+"';"

                    # FOR ALL OBJECTS
                    #qry1="SELECT id,obj_mean,obj_max,obj_area FROM "+table_hrrr+" WHERE datetime='"+str(valid)+"' and issue="+str(issue)+" and lead="+str(lead)+\
                    #   " and src='HRRR' and th="+str(th)+" and bounds='"+bounds_str+"';"
                    
                    q1=db.query(qry1)
                    cis=q1.getresult()

                    obj_count_hrrr.append(len(cis))
                    for ci in cis:
                        obj_mean.append(ci[1])
                        obj_max.append(ci[2])
                        obj_area.append(ci[3])
                        

# Area/MaxVIL distribution plots for HRRR. Comment out to have only object time series plots
'''
plot=np.asarray(obj_area)
print np.max(plot)
fig=plt.figure()
weights = np.ones_like(plot)/plot.shape[0]
#b=[0, 5, 10, 15, 20, 25, 30, 40, 50, 60,70,80,90,100]
binwidth=9
#b=np.arange(min(plot), max(plot) + binwidth, binwidth)
b=np.arange(0, 400, binwidth)
n, bins, patches = plt.hist(plot, bins=b, normed=False, facecolor='red', alpha=0.75,weights=weights)
#plt.xticks(np.arange(min(plot), max(plot) + 3*binwidth, 3*binwidth))

plt.ylim([0,0.5])
plt.ylabel('Normalized Frequency of Occurence')
#plt.xlabel('Area (km2)')
plt.xlabel('VIL (kg/m2)')
plt.title('CI Cand. MaxVIL / HRRR NE Region (4-12 July 2016)')
#plt.title('All Objects Area / HRRR NE Region (4-12 July 2016)')
plt.show()
#plt.savefig('HRRR_CIcand_Area_NE_6.png')
plt.close()
'''

##########################################################################################
#############
### CIWS ####
#############

x1, y1 = pp.map_latlon(pp.ciws(),lat1,lon1,mkInt='round')
x2, y2 = pp.map_latlon(pp.ciws(),lat2,lon2,mkInt='round')        
bounds=[(x1,y1),(x2,y2)]
bounds_str='{{'+str(x1)+','+str(y1)+'},{'+str(x2)+','+str(y2)+'}}'
dims=(str(y2-y1+2),str(x2-x1+2))    
info='lat '+str(lat1)+'-'+str(lat2)+', lon '+str(lon1)+'-'+str(lon2)

# Change Table and Field names for specific application
table_ciws='object_repo_se_18'
th=1
field='ci_15_18'

# Full Time Period
years=[2016]
months=[7]
days=[4,5,6,7,8,9,10,11]
hours=range(0,24)
minutes=range(0,60,15)

obj_max=[];obj_mean=[];obj_area=[];obj_count_ciws=[]
valid_ciws=[]
for year in years:
    for month in months:
        for day in days:
            for hour in hours:
                for minute in minutes:
                    time=datetime(year,month,day,hour,minute)
                    #print time
                    valid_ciws.append(time)
                    
                    # ONLY FOR CI CANDIDATES
                    qry1="SELECT id,obj_mean,obj_max,obj_area FROM "+table_ciws+" WHERE datetime='"+str(time)+"' and issue=999 and lead=999"+\
                       " and src='CIWS' and th="+str(th)+" and "+field+"=1 and bounds='"+bounds_str+"';"
                    
                    # FOR ALL OBJECTS
                    #qry1="SELECT id,obj_mean,obj_max,obj_area FROM "+table_ciws+" WHERE datetime='"+str(time)+"' and issue=999 and lead=999"+\
                    #   " and src='CIWS' and th="+str(th)+" and bounds='"+bounds_str+"';"
                    
                    q1=db.query(qry1)
                    cis=q1.getresult()

                    obj_count_ciws.append(len(cis))
                    for ci in cis:
                        obj_mean.append(ci[1])
                        obj_max.append(ci[2])
                        obj_area.append(ci[3])



# This part is to even out the CIWS and HRRR time series
del valid_hrrr[-8:]
del obj_count_hrrr[-8:]

for i in range(8):
    valid_ciws[i]=None
    valid_hrrr.insert(0,None)
    obj_count_ciws[i]=None
    obj_count_hrrr.insert(0,None)


# Area/MaxVIL distribution plots for CIWS. Comment out to have only object time series plots
'''
plot=np.asarray(obj_area)
print np.max(plot)

fig=plt.figure()
weights = np.ones_like(plot)/plot.shape[0]
#b=[0, 5, 10, 15, 20, 25, 30, 40, 50, 60,70,80,90,100]
binwidth=9
#b=np.arange(min(plot), max(plot) + binwidth, binwidth)
b=np.arange(0, 400, binwidth)
n, bins, patches = plt.hist(plot, bins=b, normed=False, facecolor='green', alpha=0.75,weights=weights)
#plt.xticks(np.arange(min(plot), max(plot) + 3*binwidth, 3*binwidth))

plt.ylim([0,0.5])
plt.ylabel('Normalized Frequency of Occurence')
#plt.xlabel('Area (km2)')
plt.xlabel('VIL (kg/m2)')
#plt.title('All Objects Area / CIWS NE Region (4-12 July 2016)')
plt.title('CI Cand. MaxVIL / CIWS NE Region (4-12 July 2016)')
plt.show()
#plt.savefig('CIWS_CIcand_Area_NE_6.png')
plt.close()
'''

# Object Time series plot. For both CIWS and HRRR (overlaid)
fig, ax = plt.subplots(num=None, figsize=(12, 4), dpi=80, facecolor='w', edgecolor='k')
ax.plot(obj_count_hrrr,color='r',label='HRRR')
ax.plot(obj_count_ciws,color='g',label='CIWS')
ax.set_xticks(np.arange(0,len(valid_ciws),96))
ax.set_xticklabels([4,5,6,7,8,9,10,11])
ax.legend(loc='upper left', shadow=True)
#ax.set_title('CI cand. VIL Object Count / Proximity Th = 18km')
ax.set_title('Total VIL Object Count / SE Region / Th = 1')
ax.set_ylabel('Object Count')
ax.set_xlabel('Day')
plt.ylim([0,250])
plt.show()
#plt.savefig('ObjCount_SE.png')





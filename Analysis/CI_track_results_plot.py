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

width=0.25

# NE
#ci_cand=(139.728,109.518,61.370,38.557)
#q20=(0,35.692,19.921,12.286)
#q15=(29.092,19.475,11.766,7.894)

# SE
ci_cand=(26.253,18.873,11.050,7.455)
q20=(0,9.896,6.065,4.119)
q15=(9.139,5.941,3.795,2.671)

ind = np.arange(4)

fig,ax=plt.subplots()
rects1=ax.bar(ind,ci_cand,width,color='r')
rects2=ax.bar(ind+width,q20,width,color='g')
rects3=ax.bar(ind+2*width,q15,width,color='y')

#ax.set_title('Example Case, 00:00-07:00 Z')
ax.set_title('Southeast Region, 4-12 July 2016')
ax.set_ylabel('Object Count (x1000)')
ax.set_xlabel('Previous Timestep Proximity Threshold (km)')
ax.set_xticks(ind + 1.5*width)
#ax.set_xticklabels(('6', '12', '18'))
ax.set_xticklabels(('6', '6', '12', '18'))
ax.set_ylim([0,30])
ax.legend((rects1[0], rects2[0], rects3[0]), ('CI cand.', 'VIP 3 (Q=30)', 'VIP 3 (Q=15)'))

plt.savefig('Q_sensitivity_SE.png')
#plt.show()

###########
# 5 vs 15 #
###########
'''
width=0.35
ex5=(218,183)
ex15=(23,16)
ind = np.arange(2)
fig,ax=plt.subplots()
rects1=ax.bar(ind,ex5,width,color='r')
rects2=ax.bar(ind+width,ex15,width,color='g')

ax.set_title('Example Case, 00:00-07:00 Z')
ax.set_ylabel('Object Count')
ax.set_xticks(ind + width)
ax.set_xticklabels(('CIWS 5min', 'CIWS 15min'))
ax.set_ylim([0,300])
ax.legend((rects1[0], rects2[0]), ('CI cand.', 'VIP 3'))

plt.savefig('Ex.png')

width=0.35
ex5=(3202,1810)
ex15=(239,44)
ind = np.arange(2)
fig,ax=plt.subplots()
rects1=ax.bar(ind,ex5,width,color='r')
rects2=ax.bar(ind+width,ex15,width,color='g')

ax.set_title('CONUS, 00:00-01:00 Z')
ax.set_ylabel('Object Count')
ax.set_xticks(ind + width)
ax.set_xticklabels(('CIWS 5min', 'CIWS 15min'))
ax.set_ylim([0,3500])
ax.legend((rects1[0], rects2[0]), ('CI cand.', 'VIP 3'))

plt.savefig('conus.png')
'''
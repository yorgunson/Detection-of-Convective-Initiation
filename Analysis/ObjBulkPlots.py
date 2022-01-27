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
import matplotlib as mpl
mpl.use('Qt4agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

from prod_proj import ProdProj as pp
import db_utils_CI

objcount=np.load('objcount_regions_CIWS.npy')
times=np.load('times_regions_CIWS.npy')
attrib=np.load('objatt_NE_CIWS.npy')

print len(attrib),'hed'
'''
tick_spacing = 12*24

days=list(times[0::(tick_spacing)])
day_int=[str(i.day) for i in days]
#hour_int=[4,8,12,16,20]

xticks=np.arange(0,len(times),tick_spacing)
print xticks
print times[xticks]

fig,ax=plt.subplots()
ax.plot(objcount)
#ax.locator_params(axis='x', nbins=len(day_int))
ax.set_xticks(xticks)
#ax.xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))
ax.set_xticklabels(day_int)

plt.show()
'''

'''
print np.max(attrib[:,0])

n, bins, patches = plt.hist(attrib[:,1], 200, normed=0, facecolor='green', alpha=0.75)
plt.xlim([0,100])
plt.show()
'''

import sys
sys.path.append('/mnt/user/soner.yorgun/utils')
sys.path.append('/mnt/user/soner.yorgun/CI/CI_2017/CIDetectTrack')
from time import strftime, strptime
from datetime import datetime, timedelta
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import math
from mpl_toolkits.basemap import Basemap
import matplotlib.colors as col
import matplotlib.cm as cm
from prod_proj import ProdProj as pp
from collections import OrderedDict
from matplotlib import gridspec

import db_utils_CI as db_read
import read_data

pth_plot='/mnt/user/soner.yorgun/CI/CI_2017/Plot/Plots/'

####################################################################
# THE CODE TO PLOT THE DETECTED OBJECTS NEXT TO THE ORIGINAL FIELD #
####################################################################

def Plot_VarObj(data,obj,th,objcount,dtime,latlon,xy):
    print 'hed'
    
    # Define Some Color Schemes
    custom_colors= ['white' ,'blue' ,'green' ,'yellow','red']
    nws_vil_colors = [".85",".75",".65", ".55", ".45", "#02fd02", "#fdf802", "#fd9500", "#fd0000", "#d40000", "#bc0000", "#f800fd", "#9854c6", "#483d8b"]
    awc_vil_colors = ["#A0F000", "#60B000", "#F0F000", "#F0C000", "#e09000", "#A00000"]
    cmap1 = col.ListedColormap(custom_colors,'custom1')	
    cm.register_cmap(cmap=cmap1)
    cmap2 = col.ListedColormap(awc_vil_colors, 'AWC_vil')
    cm.register_cmap(cmap=cmap2)
    cmap3 = col.ListedColormap(nws_vil_colors, 'NWS_vil')
    cm.register_cmap(cmap=cmap3)
    
    parallels = np.arange(latlon[0],latlon[1],3.)
    meridians = np.arange(latlon[2],latlon[3],3.)
        
    #PLOT
    fig,(ax2,ax1)= plt.subplots(1,2,figsize=(15, 10),gridspec_kw = {'width_ratios':[1, 1]}) 
    
    plt.suptitle('HRRR - VILTh={0} / {1} / ObjCount={2}' .format(th,dtime,objcount),size=16)
    
    #################
    # HRRR OBJ PLOT #
    #################
    #ax2=fig.add_subplot(121)
    cs1=ax2.contourf(obj,vmin=0., vmax=3.,level=[0,1,2,3,4])
    #ax2.set(adjustable='box-forced', aspect='equal')
    ax2.set_xlabel('Lon')
    ax2.set_title('Object Boundaries',size=13)
    ax2.autoscale(False)
    ax2.axis('tight')

   
    #############
    # HRRR PLOT #
    #############
    
    m1 = Basemap(llcrnrlon=latlon[2],llcrnrlat=latlon[0],urcrnrlon=latlon[3],urcrnrlat=latlon[1],resolution='l',projection='cyl')
    m1.drawstates()
    
    m1.drawparallels(parallels,labels=[True,False,False,False])
    m1.drawmeridians(meridians,labels=[False,False,False,True])
    
    ny = data_h.shape[0]; nx = data_h.shape[1]
    lons, lats = m1.makegrid(nx, ny)
    x, y = m1(lons, lats)
    
    cs=m1.contourf(x,y,data,levels=[0,1,3.5,4,5,6,8,10],cmap='NWS_vil')
    ax1.set_title('HRRR',size=13)
    ax1.axis('tight')
    plt.colorbar(cs,fraction=0.07, pad=0.03)
    
    plt.subplots_adjust(left=0.05, right=0.95, top=0.9, bottom=0.05)
    
    #plt.show()
    plt.savefig(pth_plot+'HRRRobj2_{0}_nosizeTH_15_evol_{1}.png' .format(dtime,th))
    
    return


if "__main__" == __name__:
    
    src1='HRRR'
    config_h= __import__('config_CI_'+src1)
    
    # Define Bounds
    bounded='yes'
    
    if bounded=='yes':

        #lat1=30;lat2=33;lon1=-105;lon2=-102.5
        #lat1=40;lat2=47;lon1=-122;lon2=-107
        lat1=37;lat2=43;lon1=-105;lon2=-99 #HRRR Bounds
        
        x1_h, y1_h = pp.map_latlon(pp.hrrr(),lat1,lon1,mkInt='round')
        x2_h, y2_h = pp.map_latlon(pp.hrrr(),lat2,lon2,mkInt='round')
        bounds_h='{{'+str(x1_h)+','+str(y1_h)+'},{'+str(x2_h)+','+str(y2_h)+'}}'
        
    else:
        lat1=config_h.lat1;lat2=config_h.lat2;lon1=config_h.lon1;lon2=config_h.lon2
        x1_h, y1_h = pp.map_latlon(pp.hrrr(),lat1,lon1,mkInt='round')
        x2_h, y2_h = pp.map_latlon(pp.hrrr(),lat2,lon2,mkInt='round')
        bounds_h='{999}'
    
    # Time info
    '''
    years=[2016]
    months=[5]#[4]
    days=[8]#[1]
    hours=[0,1,2,3,4,5,6]#[0,1,2,3,4,5,6]
    #minutes=[0,5,10,15,20,25,30,35,40,45,50,55]
    minutes=[0,15,30,45]
    '''
    
    years=[2016]
    months=[6]
    days=[4]#,5,6,7,8,9,10,11,12,13,14,15,16,17,18]
    issues=range(0,24)
    leads=range(0,495,15)

    th=1
    
    # Connect to the database
    #db=db_read.get_conn(config.hostname, config.username, config.password, config.database)
    
    # For each time step, read the database and plot
    for year in years:
        for month in months:
            for day in days:
                for issue in issues:
                    for ld in leads:
                        
                        #HRRR Time info
                        ld=str(hour).zfill(2)+str(minute).zfill(2)
                        time_h=OrderedDict([('year',year),('month',month),('day',day),('issue',hours[0]),('lead',ld)])
                        valid_h=OrderedDict([('year',year),('month',month),('day',day),('issue',hour),('lead',minute)])
                        issue_h=int(hours[0])
                        lead_h=int(ld)
        
                        ncfile_data_h = read_data.get_file(config_h.DataFile(time_h),config_h.filetype)
                        data_h=np.squeeze(ncfile_data_h.variables[config_h.variable])
                        
                        if bounded=='yes':
                            data_h=data_h[y1_h:y2_h,x1_h:x2_h]
                            obj_h=np.zeros((y2_h-y1_h+2,x2_h-x1_h+2))
                        else:
                            lat1_h=config_h.lat1;lat2_h=config_h.lat2;lon1_h=config_h.lon1;lon2_h=config_h.lon2
                            y2_h=config_h.y;y1_h=0;x2_h=config_h.x;x1=0

                            obj_h=np.zeros((data_h.shape[0],data_h.shape[1]))
                        
                        dtime=datetime(year,month,day,hour,minute)
                        
                        # HRRR Object Stuff from the database
                        
                        db=db_read.get_conn(config_h.hostname, config_h.username, config_h.password, config_h.database)
                        
                        objcount_h=db_read.get_ObjCount(db,config_h.obj_table,src1,dtime,issue_h,lead_h,0,th,bounds_h)
                        obj_ij_h=db_read.get_AllObjij(db,config_h.obj_table,src1,dtime,issue_h,lead_h,0,th,bounds_h)
                        cmass_h=db_read.get_AllObjCmass(db,config_h.obj_table,src1,dtime,issue_h,lead_h,0,th,bounds_h)
                        
                        obj_ciij_h=db_read.get_CIObjij(db,config_h.obj_table,src1,dtime,issue_h,lead_h,0,th,bounds_h,'ci_15')
                        obj_ciij_evol_h=db_read.get_CIObjij(db,config_h.obj_table,src1,dtime,issue_h,lead_h,0,th,bounds_h,'ci_evol_15')

                        
                        obj_h[obj_ij_h[:,0],obj_ij_h[:,1]]=1
                        if len(obj_ciij_evol_h)>0:obj_h[obj_ciij_evol_h[:,0],obj_ciij_evol_h[:,1]]=2
                        if len(obj_ciij_h)>0:obj_h[obj_ciij_h[:,0],obj_ciij_h[:,1]]=3
                        
                        latlon=(lat1,lat2,lon1,lon2)
                        xy_h=(y1_h,y2_h,x1_h,x2_h)
                        
                        objcount_h=0
                        Plot_VarObj(data_h,obj_h,th,objcount_h,dtime,latlon,xy_h)




 
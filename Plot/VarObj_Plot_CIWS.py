import sys
sys.path.append('/mnt/user/soner.yorgun/utils')
sys.path.append('/mnt/user/soner.yorgun/CI/CI_2017/CIDetectTrack')
from time import strftime, strptime
from datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt
import math
from mpl_toolkits.basemap import Basemap
import matplotlib.colors as col
import matplotlib.cm as cm
from prod_proj import ProdProj as pp
from collections import OrderedDict
from matplotlib import gridspec
import matplotlib as mpl
mpl.use('Qt4agg')

import db_utils_CI as db_read
import read_data

pth_plot='/mnt/user/soner.yorgun/CI/CI_2017/Plot/Plots/'

####################################################################
# THE CODE TO PLOT THE DETECTED OBJECTS NEXT TO THE ORIGINAL FIELD #
####################################################################

def Plot_VarObj(data,obj,th,objcount,dtime,latlon,xy):
    
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
    
    plt.suptitle('CIWS - VILTh={0} / {1} / ObjCount={2}' .format(th,dtime,objcount),size=16)
    
    #################
    # CIWS OBJ PLOT #
    #################
    #ax2=fig.add_subplot(121)
    cs1=ax2.contourf(obj,vmin=0., vmax=3.,level=[0,1,2,3,4])
    #ax2.set(adjustable='box-forced', aspect='equal')
    ax2.set_xlabel('Lon')
    ax2.set_title('Object Boundaries',size=13)
    ax2.autoscale(False)
    ax2.axis('tight')
   
    #############
    # CIWS PLOT #
    #############
    
    m1 = Basemap(llcrnrlon=latlon[2],llcrnrlat=latlon[0],urcrnrlon=latlon[3],urcrnrlat=latlon[1],resolution='l',projection='cyl')
    m1.drawstates()
    
    m1.drawparallels(parallels,labels=[True,False,False,False])
    m1.drawmeridians(meridians,labels=[False,False,False,True])
    
    ny = data_c.shape[0]; nx = data_c.shape[1]
    lons, lats = m1.makegrid(nx, ny)
    x, y = m1(lons, lats)
    
    cs=m1.contourf(x,y,data,levels=[0,1,3.5,4,5,6,8,10],cmap='NWS_vil')
    ax1.set_title('CIWS',size=13)
    ax1.axis('tight')
    plt.colorbar(cs,fraction=0.07, pad=0.03)
    
    plt.subplots_adjust(left=0.05, right=0.95, top=0.9, bottom=0.05)
    
    #plt.show()
    #plt.savefig(pth_plot+'CIWSobj_{0}_5_evol_{1}.png' .format(dtime,th))
    #plt.savefig(pth_plot+'CIWSexample_15min_18km_{0}.png' .format(dtime))
    plt.savefig(pth_plot+'CIWSq40_{0}_15_evol_{1}.png' .format(dtime,th))
    
    return


if "__main__" == __name__:
    
    src1='CIWS'
    config_c= __import__('config_CI_'+src1)
    
    # Define Bounds
    bounded='yes'
    
    if bounded=='yes':
        #lat1=30;lat2=40;lon1=-105;lon2=-95
        #lat1=30;lat2=36;lon1=-105;lon2=-99
        #lat1=30;lat2=33;lon1=-105;lon2=-102.5
        lat1=34;lat2=47;lon1=-90;lon2=-66 # NE Region Bounds
        
        x1_c, y1_c = pp.map_latlon(pp.ciws(),lat1,lon1,mkInt='round')
        x2_c, y2_c = pp.map_latlon(pp.ciws(),lat2,lon2,mkInt='round')
        bounds_c='{{'+str(x1_c)+','+str(y1_c)+'},{'+str(x2_c)+','+str(y2_c)+'}}'
        
    else:
        bounds='{999}'
    
    # Time info
    
    years=[2016]
    months=[7]
    days=[4]#,6,7,8,9,10,11,12,13,14,15,16,17,18,19]
    hours=range(0,2)
    minutes=range(0,60,15)
    '''
    
    # Example Time Period
    years=[2015]
    months=[5]
    days=[5]
    hours=range(0,3)#7)
    #hours=[0]
    minutes=range(0,60,5)
    #minutes=[5,10]
    '''
    issue=999
    lead=999
    th=1
    
    # For each time step, read the database and plot
    for year in years:
        for month in months:
            for day in days:
                for hour in hours:
                    for minute in minutes:
                        
                        time_c=OrderedDict([('year',year),('month',month),('day',day),('hour',hour),('minute',minute)])
                        dtime=datetime(year,month,day,hour,minute)
        
                        
                        ncfile_data_c = read_data.get_file(config_c.DataFile(time_c),config_c.filetype)
                        data_c=np.squeeze(ncfile_data_c.variables[config_c.variable])
                        
                        if bounded=='yes':
                            data_c=data_c[y1_c:y2_c,x1_c:x2_c]
                            obj_c=np.zeros((y2_c-y1_c+2,x2_c-x1_c+2))
                            
                        else:
                            lat1_c=config_c.lat1;lat2_c=config_c.lat2;lon1_c=config_c.lon1;lon2_c=config_c.lon2
                            y2_c=config_c.y;y1_c=0;x2_c=config_c.x;x1=0
                            
                            obj_c=np.zeros((data_c.shape[0],data_c.shape[1]))
                        
                        
                        # CIWS Object Stuff from the database
                        
                        db=db_read.get_conn(config_c.hostname, config_c.username, config_c.password, config_c.database)
                        
                        objcount_c=db_read.get_ObjCount(db,config_c.obj_table,src1,dtime,issue,lead,0,th,bounds_c)
                        obj_ij_c=db_read.get_AllObjij(db,config_c.obj_table,src1,dtime,issue,lead,0,th,bounds_c)
                        cmass_c=db_read.get_AllObjCmass(db,config_c.obj_table,src1,dtime,issue,lead,0,th,bounds_c)
                        
                        obj_ciij_c=db_read.get_CIObjij(db,config_c.obj_table,src1,dtime,issue,lead,0,th,bounds_c,'ci_15_18')
                        obj_ciij_evol_c=db_read.get_CIObjij(db,config_c.obj_table,src1,dtime,issue,lead,0,th,bounds_c,'ci_evol_15_18q15')
                        
                        print dtime
                        obj_c[obj_ij_c[:,0],obj_ij_c[:,1]]=1
                        if len(obj_ciij_evol_c)>0:obj_c[obj_ciij_evol_c[:,0],obj_ciij_evol_c[:,1]]=2
                        if len(obj_ciij_c)>0:obj_c[obj_ciij_c[:,0],obj_ciij_c[:,1]]=3
                        

                        latlon=(lat1,lat2,lon1,lon2)
                        xy_c=(y1_c,y2_c,x1_c,x2_c)
                        
                        Plot_VarObj(data_c,obj_c,th,objcount_c,dtime,latlon,xy_c)




 
import sys
sys.path.append('/mnt/user/soner.yorgun/utils')
sys.path.append('/mnt/user/soner.yorgun/CI/CI_2017/ConfigFiles')
from time import strftime, strptime
from datetime import datetime, timedelta
import numpy as np
import math
import numpy.ma as ma
import random
from collections import OrderedDict
from pg import DB
import re

from prod_proj import ProdProj as pp
import read_data


#################################################
# CLASS FOR OBJECT DETECTION AND OBJECT STORAGE #
#################################################

class ObjDetectAtt(object):
    
    
    def __init__(self,src,time,issue,lead,bounds,dims): # Initialization of the object detection instance.
        
        # src = product name
        # time = dictionary containing product specific time information 

        self.config= __import__('config_CI_'+src)
        
        # Check if the time dictionary is entered correctly
        if sorted(self.config.timekeys) != sorted(time.keys()):
            raise Exception('Time information mismatch!')
        
        # Set variable
        self.variable=self.config.variable
        
        # Read Data
        # Currently the algorithm only handles a 2D lat/lon grid so the data is squeezed to drop single sized axes
        
        self.ncfile_data= read_data.get_file(self.config.DataFile(time),self.config.filetype)
        self.data=np.squeeze(self.ncfile_data.variables[self.variable])
        self.ncfile_data.close()
        
        if bounds==[999]:
            self.dim1=str(self.data.shape[0]+2);self.dim2=str(self.data.shape[1]+2)
            
        else:   
            self.y1=bounds[0][1];self.y2=bounds[1][1]
            self.x1=bounds[0][0];self.x2=bounds[1][0]
            self.dim1=dims[0];self.dim2=dims[1]
            
            self.data=self.data[self.y1:self.y2,self.x1:self.x2]
         
            
        return
    
        
    def RegGrow(self,th):
        
        self.th=th
        
        # Initiate the array to hold identified objects
        self.objects=np.zeros(1, dtype=[('obj_labels','('+self.dim1+','+self.dim2+')int'),
                                        ('obj_Var','('+self.dim1+','+self.dim2+')float'),
                                        ('total_Var','('+self.dim1+','+self.dim2+')float')])
        
        # Pad zeros to boundaries for object detection
        self.data=np.pad(self.data, ((1,1),(1,1)), 'constant', constant_values=(0,)) 
        self.data_th=np.copy(self.data)
    
        # Populate the total_var field of the array (THIS DOESN'T GO TO DB)
        self.objects['total_Var'][0,:,:]=self.data
        
        # Threshold the data array and make it binary
        np.place(self.data_th, self.data_th>=self.th, 100)
        np.place(self.data_th, self.data_th<self.th, 0)
        np.place(self.data_th, self.data_th>0, 1)
        
        # Duplicate the data array to work on
        self.data_work=np.copy(self.data_th)
                    
        bigdec=0 # Decision to stop the while loop that finds all objects for a given time and location
        rcount=0 # The labels of the objects
        self.obj_ij=[]
        while bigdec==0:
            
            # Get all the gridpoints that satisfy the threshold  
            pick=np.argwhere(self.data_work==1)
            
            # If there is no gridpoints to satisfy the data threshold (i.e., no objects) break the loop
            if len(pick)==0:
                break
            
            # Pick a random gridpoint with VIL>=th
            # We don't want the first pick at the boundary (reason of the problem unknown yet)
            ii=1;jj=1;ct=0
            while ii==1 or jj==1:
                a=np.random.choice(np.arange(pick.shape[0]),1)
                ii=pick[a[0]][0]
                jj=pick[a[0]][1]
                ct+=1
                if ct==100:break
            
            # Initiate the object count and recording
            rcount+=1
            self.objects['obj_labels'][0,ii,jj]=rcount
            self.data_work[ii,jj]=0
            iter_list=[]
            final_ij_list=[]
            iter_list.append((ii,jj))
            final_ij_list.append((ii,jj))
            
            # The loop to search the adjacent gridpoints until a single object is formed
            dec=0
            while dec==0:
                declist=[]
                iter_list_new=[]
                for idx in iter_list:
                    for i,j in self.config.iterator:
                        
                        # If the search ij is not outside the grid
                        if idx[0]-i>0 and idx[0]+i<self.data_th.shape[0] and idx[1]-j>0 and idx[1]+j<self.data_th.shape[1]:
                            
                            # If the gridpoint is not labeled yet
                            if self.objects['obj_labels'][0,idx[0]+i,idx[1]+j]==0:
                                
                                if self.data_th[idx[0]+i,idx[1]+j]==1:
                                    self.objects['obj_labels'][0,idx[0]+i,idx[1]+j]=rcount
                                    self.data_work[idx[0]+i,idx[1]+j]=0
                                    declist.append(0)
                                    iter_list_new.append((idx[0]+i,idx[1]+j))
                                    final_ij_list.append((idx[0]+i,idx[1]+j))
                                else:    
                                    declist.append(1)
                            
                iter_list=iter_list_new
                
                # Check if the single object is wholly identified
                check=np.unique(np.asarray(declist))
                if check.shape[0]>1:
                    dec=0
                elif check==1:
                    dec=1
                elif check==0:
                    dec=0        
            
            self.obj_ij.append(final_ij_list)

            # Check if all the objects in the field is identified
            if np.any(self.data_work)==1:
                bigdec=0
            else:
                bigdec=1
        
        #print np.max(np.unique(self.objects['obj_labels'][0,:,:])), 'objects detected...'
        
        for i in range(self.objects['obj_labels'].shape[1]):
            for j in range(self.objects['obj_labels'].shape[2]):
                if self.objects['obj_labels'][0,i,j]!=0:
                    self.objects['obj_Var'][0,i,j]=self.data[i,j]
         
        
        return self.objects,self.obj_ij
    
    @staticmethod
    def Attrb(config,objects):
        
        #print "Computing object attributes..."
            
        # Initiate the attribute array
        maxnum=np.max(objects['obj_labels']) #determine the maximum number of objects to be able to form the array
        adim=str(maxnum)
        attrib=np.zeros(objects.shape[0], dtype=[('obj_num','('+adim+',)int'),
                                                ('area','('+adim+',)int'),
                                                ('cmass','('+adim+',2)int'),
                                                ('maxVar','('+adim+',)float'),
                                                ('meanVar','('+adim+',)float')])
  
        objnums=np.unique(objects['obj_labels'][0,:,:]) # Get the number of identifed objects (for each timestep) 
        objnums=np.delete(objnums,0) # Delete the initial number, which is zero

        # For each object do
        for j in range(len(objnums)):
            
            # Get the gridpoints that are labeled with the corresponding object number
            # CAN BE SPED UP
            count=np.argwhere(objects['obj_labels'][0,:,:]==objnums[j])
            
            # Calculate the center of mass and mean/max VIL of the corresponding object
            mass=[]
            mass_x=[]
            mass_y=[]
            for k in range(len(count)):
                mass.append(objects['obj_Var'][0,count[k][0],count[k][1]])
                mass_x.append(count[k][0]*objects['obj_Var'][0,count[k][0],count[k][1]])
                mass_y.append(count[k][1]*objects['obj_Var'][0,count[k][0],count[k][1]])
            
            cmass_x=round(sum(mass_x)/sum(mass))
            cmass_y=round(sum(mass_y)/sum(mass))
            
            meanVar=sum(mass)/len(mass)
            maxVar=max(mass)
            
            # Populate the attribute array
            attrib['obj_num'][0][j]=objnums[j]
            attrib['area'][0][j]=len(count)*config.area_coeff
            attrib['cmass'][0][j][0]=cmass_x
            attrib['cmass'][0][j][1]=cmass_y
            attrib['meanVar'][0][j]=meanVar
            attrib['maxVar'][0][j]=maxVar
            
        return attrib
    
    @staticmethod
    def db_write(src,time,issue,lead,level,th,obj_ij,attrib,bounds,info):
        
        #print "Writing stuff to dB..."
        
        #dtime=datetime(*map(int,time.values()))
        
        # Get Connection
        config= __import__('config_CI_'+src)
        db = DB(dbname=config.database, host=config.hostname, user=config.username, passwd=config.password)        
        
        for i in range(len(attrib['obj_num'][0])):
        
            # Revert the array data into proper Postgress format
            # Very primitive way of writing the data. It needs to be replaced by a better method
            objij=re.sub('[[(]','{',str(obj_ij[i]))
            objij=re.sub('[])]','}',objij)
            
            objcmass=re.sub('[[(]','{',str([(attrib['cmass'][0][i][0],attrib['cmass'][0][i][1])]))
            objcmass=re.sub('[])]','}',objcmass)
            
            bounds=re.sub('[[(]','{',str(bounds))
            bounds=re.sub('[])]','}',bounds)
            
            # Write Data    
            db.insert(config.obj_table,
                      src=src,
                      datetime=time,
                      issue=issue,
                      lead=lead,
                      level=level,
                      th=th,
                      obj_type=config.variable,
                      obj_num=attrib['obj_num'][0][i],
                      obj_ij=objij,
                      obj_cmass=objcmass,
                      obj_area=attrib['area'][0][i],
                      obj_mean=attrib['meanVar'][0][i],
                      obj_max=attrib['maxVar'][0][i],
                      info=info,
                      bounds=bounds,
                      )
    
        return
        
        
################
#     MAIN     #
################
if "__main__" == __name__:
    
    years=[2015]
    months=[5]#[4]
    days=[5]#[1]
    hours=[0,1,2,3,4,5,6]
    minutes=[0,5,10,15,20,25,30,35,40,45,50,55]
    
    src='CIWS'
    issue=999
    lead=999
    th=3.5
    
    # CIWS Area Bound
    ################################
    bounded=True
    #lat1=38.2;lat2=39.6;lon1=-98.3;lon2=-97
    lat1=30;lat2=40;lon1=-105;lon2=-95

    if bounded==False:
        bounds=[999]
        dims=[999]
        info=''
            
    elif bounded==True:
                        
        x1, y1 = pp.map_latlon(pp.ciws(),lat1,lon1,mkInt='round')
        x2, y2 = pp.map_latlon(pp.ciws(),lat2,lon2,mkInt='round')        
        bounds=[(x1,y1),(x2,y2)]
        dims=(str(y2-y1+2),str(x2-x1+2))
        info='lat '+str(lat1)+'-'+str(lat2)+', lon '+str(lon1)+'-'+str(lon2)
    
    for year in years:
        for month in months:
            for day in days:
                for hour in hours:
                    for minute in minutes:
                        
                        dt=OrderedDict([('year',year),('month',month),('day',day),('hour',hour),('minute',minute)])
                        
                        print datetime(year,month,day,hour,minute)
                    
                        ciws_inst=ObjDetectAtt(src,dt,issue,lead,bounds,dims)
                        objects,obj_ij=ciws_inst.RegGrow(th)
                        attrib=ciws_inst.Attrb(objects)
                        ciws_inst.db_write(src,dt,issue,lead,0,th,obj_ij,attrib,bounds,info)
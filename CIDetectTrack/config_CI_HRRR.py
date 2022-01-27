#####################################################
## Configuration File for CIWS data for CI Project ##
#####################################################

# Database Information
#####################################################################################
hostname='fvs-anb2'
database='object_soner'
username='nevsoper'
password=''
#obj_table='object_repo_regions_HRRR'
obj_table='object_repo_ne_hrrr_q15'
#obj_table='object_repo_mtom'

# CI/CIWS Path Information 
###############################
pth_hrrr='/mnt/view/event/hrrr_raw/'

# The iteration list that will check adjacent cells for the region growing method
# (No need to change according to File or Project)
####################################################################################
list_i=[1,1,1,0,0,0,-1,-1,-1]
list_j=[-1,0,1,-1,0,1,-1,0,1,]
iterator=zip(list_i,list_j)

# CIWS Time information
################################
timekeys=['year','month','day','issue','lead']
timedict={key: None for key in timekeys}
timestep=15 #in minutes (lead)

# CIWS Datafile information
################################
filetype='netcdf'

def DataFile(tdict):
    datafile=pth_hrrr+str(tdict[timekeys[0]])+'/'+str(tdict[timekeys[1]]).zfill(2)+'/'+str(tdict[timekeys[2]]).zfill(2)+'/'+ \
             str(tdict[timekeys[0]])+str(tdict[timekeys[1]]).zfill(2)+str(tdict[timekeys[2]]).zfill(2)+ \
             '_'+str(tdict[timekeys[3]]).zfill(2)+'0000_'+str(tdict[timekeys[4]]).zfill(4)+'00.ncf.gz'
    return datafile


# CIWS Variable and Domain and Info
################################
variable='Vertically_Integrated_Water'

# Latitude/Longitude Bounds for the product
lat1=19.35
lat2=48.82
lon1=-122.39
lon2=-62.02

# Gridsize of the product
y=1059
x=1799

# CI Detection Thresholds
size_th=250 # Size threshold
#dist_th=25 # Edge-to-edge distance threshold
prev_th=18 # The threshold to define if a candidate CI existed in the previous timestep

area_coeff=9 # Approx. Gridsize to calculate areas

# Tracking coefficients
MBS_HalfSide = 10 # Initial bounding square (BS) side half-length
Q = 15 # Tracking cutoff
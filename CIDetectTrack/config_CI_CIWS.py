#####################################################
## Configuration File for CIWS data for CI Project ##
#####################################################

# Database Information
#####################################################################################
hostname='fvs-anb2'
database='object_soner'
username='nevsoper'
password=''
#obj_table='object_repo_regions'
obj_table='object_repo_se_6'

# CI/CIWS Path Information 
###############################
pth_vil='/mnt/view/mrms_ciws/ciws_vil_1km/'
pth_et='/mnt/view/mrms_ciws/ciws_echo_top_1km/'
pth_plot='/mnt/user/soner.yorgun/CI/CI_2017/Plots/'
pth_array='/mnt/user/soner.yorgun/CI/SavedArrays/'

# The iteration list that will check adjacent cells for the region growing method
# (No need to change according to File or Project)
####################################################################################
list_i=[1,1,1,0,0,0,-1,-1,-1]
list_j=[-1,0,1,-1,0,1,-1,0,1,]
iterator=zip(list_i,list_j)

# CIWS Time information
################################
timekeys=['year','month','day','hour','minute']
timedict={key: None for key in timekeys}
timestep=15 #in minutes

# CIWS Datafile information
################################
filetype='netcdf'

def DataFile(tdict):
    datafile=pth_vil+str(tdict[timekeys[0]])+'/'+str(tdict[timekeys[1]]).zfill(2)+'/'+str(tdict[timekeys[2]]).zfill(2)+'/'+ \
             str(tdict[timekeys[0]])+str(tdict[timekeys[1]]).zfill(2)+str(tdict[timekeys[2]]).zfill(2)+ \
             '_'+str(tdict[timekeys[3]]).zfill(2)+str(tdict[timekeys[4]]).zfill(2)+'00.ncf.gz'
    return datafile


# CIWS Variable and Domain and Info
###################################
variable='VIL'

# Latitude/Longitude Bounds for the product
lat1=19.35
lat2=48.82
lon1=-122.39
lon2=-62.02

# Gridsize of the product
y=3500
x=5100

# Thresholds
#############

# CI Detection Thresholds
size_th=250 # Size threshold (larger than this will not be considered for CI, to reduce computational complexity)
#dist_th=10 # Edge-to-edge distance threshold
prev_th=6 # The threshold to define if a candidate CI existed in the previous timestep

area_coeff=1 # Approx. Gridsize to calculate areas

# Tracking coefficients
MBS_HalfSide = 30 # Initial bounding square (BS) side half-length
Q = 30 # Tracking cutoff
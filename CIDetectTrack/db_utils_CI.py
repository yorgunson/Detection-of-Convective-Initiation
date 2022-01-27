from pg import DB
import numpy as np
import re
from datetime import datetime, timedelta
from time import strftime, strptime



# Get Database Connection
def get_conn(hostname, username, password, dbname):
    db = DB(dbname=dbname, host=hostname, user=username, passwd=password)
    return db


def get_ObjCount(db,table,src,dtime,issue,lead,level,th,bounds):
    
    qry="SELECT distinct obj_num FROM "+table+" WHERE datetime='"+str(dtime)+"' and src='"+src+"' and issue="+str(issue)+" and lead="+str(lead)+\
        " and level="+str(level)+" and th="+str(th)+" and bounds='"+str(bounds)+"';"
    
    q=db.query(qry)
    objnums=q.getresult()

    if len(objnums)==0:maxobj=0
    else:maxobj=max(objnums)[0]
    
    return maxobj


# Read Object ij for all the Objects in the Field
def get_AllObjij(db,table,src,dtime,issue,lead,level,th,bounds):
    
    qry="SELECT unnest(obj_ij) FROM "+table+" WHERE datetime='"+str(dtime)+"' and src='"+src+"' and issue="+str(issue)+" and lead="+str(lead)+\
        " and level="+str(level)+" and th="+str(th)+" and bounds='"+str(bounds)+"';"
    
    q=db.query(qry)
    flat=q.getresult()
    obj_ij=np.asarray([flat[i]+flat[i+1] for i in range(0,len(flat),2)])
    
    return obj_ij


# Read Object ij for a Single Object
def get_SingleObjij(db,table,src,dtime,issue,lead,level,th,objnum,bounds):
    
    qry="SELECT unnest(obj_ij) FROM "+table+" WHERE datetime='"+str(dtime)+"' and src='"+src+"' and issue="+str(issue)+" and lead="+str(lead)+\
        " and level="+str(level)+" and th="+str(th)+" and bounds='"+str(bounds)+"' and obj_num="+str(objnum)+";"
    
    q=db.query(qry)
    flat=q.getresult()
    obj_ij=[flat[i]+flat[i+1] for i in range(0,len(flat),2)]
    
    return obj_ij


# Read Object cmass for all the Objects in the Field satisfying a size threshold
def get_AllObjCmass_Area(db,table,src,dtime,issue,lead,level,th,bounds,area,info):
    
    qry="SELECT unnest(obj_cmass) FROM "+table+" WHERE datetime='"+str(dtime)+"' and src='"+src+"' and issue="+str(issue)+" and lead="+str(lead)+\
        " and level="+str(level)+" and th="+str(th)+" and bounds='"+str(bounds)+"' and obj_area"+info+str(area)+";"
    
    q=db.query(qry)
    flat=q.getresult()
    obj_cmass=[flat[i]+flat[i+1] for i in range(0,len(flat),2)]
    
    return obj_cmass


# Read Object ij for a Single Object using cmass
def get_SingleObjij_Cmass(db,table,src,dtime,issue,lead,level,th,cmass,bounds):
    
    cmass=re.sub('[[(]','{',str(cmass))
    cmass=re.sub('[])]','}',cmass)
    
    qry="SELECT unnest(obj_ij) FROM "+table+" WHERE datetime='"+str(dtime)+"' and src='"+src+"' and issue="+str(issue)+" and lead="+str(lead)+\
        " and level="+str(level)+" and th="+str(th)+" and bounds='"+str(bounds)+"' and obj_cmass='{"+cmass+"}';"
    
    q=db.query(qry)
    flat=q.getresult()
    obj_ij=[flat[i]+flat[i+1] for i in range(0,len(flat),2)]
    
    return obj_ij

# Read Object ij for a Single Object using ID
def get_SingleObjij_id(db,table,objid):
    
    qry="SELECT unnest(obj_ij) FROM "+table+" WHERE id="+str(objid)+";"
    
    q=db.query(qry)
    flat=q.getresult()
    obj_ij=[flat[i]+flat[i+1] for i in range(0,len(flat),2)]
    
    return obj_ij

# Read Object cmass for all the Objects in the Field
def get_AllObjCmass(db,table,src,dtime,issue,lead,level,th,bounds):
    
    qry="SELECT unnest(obj_cmass) FROM "+table+" WHERE datetime='"+str(dtime)+"' and src='"+src+"' and issue="+str(issue)+" and lead="+str(lead)+\
        " and level="+str(level)+" and th="+str(th)+" and bounds='"+str(bounds)+"';"
    
    q=db.query(qry)
    flat=q.getresult()
    obj_cmass=np.asarray([flat[i]+flat[i+1] for i in range(0,len(flat),2)])
    
    return obj_cmass


# Read All the Obj information given src, time, th and bounds
def get_allObj(db,table,src,dtime,th,bounds):
    
    ret=[]
    
    qry="SELECT datetime,obj_cmass,issue,lead,level,obj_type,obj_area,obj_max,obj_mean FROM "+table+" WHERE datetime='"+str(dtime)+\
        "' and src='"+src+"' and th="+str(th)+"and bounds='"+str(bounds)+"';"
    
    q=db.query(qry)
    ci=q.getresult()
    for i in range(len(ci)):
        cmass=ci[i][1].replace('{','').replace('}','').split(',')
        ret.append([datetime.strptime(ci[i][0], '%Y-%m-%d %H:%M:%S'),(int(cmass[0]),int(cmass[1])),ci[i][6],ci[i][7],ci[i][8]])
        
    return ret

# Read All the Obj information WITHIN AN AREA given src, time, th and bounds
def get_allObj_MBS(db,table,src,dtime,th,bounds,refcmass,MBS_HalfSide):
    
    ret=[]
    
    y2=refcmass[0]+MBS_HalfSide
    y1=refcmass[0]-MBS_HalfSide
    x2=refcmass[1]+MBS_HalfSide
    x1=refcmass[1]-MBS_HalfSide
    
    qry="SELECT datetime,obj_cmass,issue,lead,level,obj_area,obj_max,id FROM "+table+" WHERE datetime='"+str(dtime)+"' and src='"+src+"' and th="+str(th)+\
        "and bounds='"+str(bounds)+"' and obj_cmass[1][1]<"+str(y2)+" and obj_cmass[1][1]>"+str(y1)+" and obj_cmass[1][2]<"+str(x2)+" and obj_cmass[1][2]>"+str(x1)+";"
    
    q=db.query(qry)
    ci=q.getresult()
    for i in range(len(ci)):
        cmass=ci[i][1].replace('{','').replace('}','').split(',')
        ret.append([datetime.strptime(ci[i][0], '%Y-%m-%d %H:%M:%S'),int(cmass[0]),int(cmass[1]),ci[i][5],ci[i][6],ci[i][7]])
        
    return ret

# Read All the Obj information WITHIN AN AREA given src, time, th and bounds
def get_allObj_MBS_hrrr(db,table,src,dtime,issue,lead,th,bounds,refcmass,MBS_HalfSide):
    
    ret=[]
    
    y2=refcmass[0]+MBS_HalfSide
    y1=refcmass[0]-MBS_HalfSide
    x2=refcmass[1]+MBS_HalfSide
    x1=refcmass[1]-MBS_HalfSide
    
    qry="SELECT datetime,obj_cmass,issue,lead,level,obj_area,obj_max,id FROM "+table+" WHERE datetime='"+str(dtime)+"' and issue="+str(issue)+" and lead="+str(lead)+" and src='"+src+"' and th="+str(th)+\
        "and bounds='"+str(bounds)+"' and obj_cmass[1][1]<"+str(y2)+" and obj_cmass[1][1]>"+str(y1)+" and obj_cmass[1][2]<"+str(x2)+" and obj_cmass[1][2]>"+str(x1)+";"
    
    q=db.query(qry)
    ci=q.getresult()
    for i in range(len(ci)):
        cmass=ci[i][1].replace('{','').replace('}','').split(',')
        ret.append([datetime.strptime(ci[i][0], '%Y-%m-%d %H:%M:%S'),int(cmass[0]),int(cmass[1]),ci[i][5],ci[i][6],ci[i][7]])
        
    return ret

##################
##################
## CI STUFF ######
##################


# Read Object ij for CI Objects in the Field (if any)
def get_CIObjij(db,table,src,dtime,issue,lead,level,th,bounds,field):
    
    qry="SELECT unnest(obj_ij) FROM "+table+" WHERE "+field+"=1 and datetime='"+str(dtime)+"' and src='"+src+"' and issue="+str(issue)+" and lead="+str(lead)+\
        " and level="+str(level)+" and th="+str(th)+" and bounds='"+str(bounds)+"';"
    
    q=db.query(qry)
    flat=q.getresult()
    obj_ciij=np.asarray([flat[i]+flat[i+1] for i in range(0,len(flat),2)])
    
    return obj_ciij


# Read All the CI information given src, th and bounds (ALL TIMES)
'''
def get_allCI(db,table,src,th,bounds):
    
    ret=[]
    
    qry="SELECT datetime,obj_cmass,issue,lead,level,obj_type,obj_area,obj_max,obj_mean FROM "+table+" WHERE src='"+src+\
        "' and th="+str(th)+" and ci=1 and bounds='"+str(bounds)+"';"
    
    q=db.query(qry)
    ci=q.getresult()
    for i in range(len(ci)):
        cmass=ci[i][1].replace('{','').replace('}','').split(',')
        ret.append([datetime.strptime(ci[i][0], '%Y-%m-%d %H:%M:%S'),(int(cmass[0]),int(cmass[1])),ci[i][6],ci[i][7],ci[i][8]])
        
    return ret
'''

# Read All the CI information given src, th and bounds
def get_allCI(db,table,src,dtime,th,bounds,field):
    
    ret=[];ci_id=[]
    
    qry="SELECT obj_cmass,issue,lead,level,obj_type,obj_area,obj_max,obj_mean,id FROM "+table+" WHERE datetime='"+str(dtime)+"' and src='"+src+\
        "' and th="+str(th)+" and "+field+"=1 and bounds='"+str(bounds)+"';"
    
    q=db.query(qry)
    ci=q.getresult()
    for i in range(len(ci)):
        cmass=ci[i][0].replace('{','').replace('}','').split(',')
        ret.append([(int(cmass[0]),int(cmass[1])),ci[i][5],ci[i][6],ci[i][7]])
        ci_id.append(ci[i][8])
        
    return ret,ci_id

# Read All the CI information given src, th and bounds
def get_allhrrrCI(db,table,src,dtime,issue,lead,th,bounds,field):
    
    ret=[];ci_id=[]
    
    qry="SELECT obj_cmass,issue,lead,level,obj_type,obj_area,obj_max,obj_mean,id FROM "+table+" WHERE datetime='"+str(dtime)+\
    "' and issue="+str(issue)+" and lead="+str(lead)+" and src='"+src+"' and th="+str(th)+" and "+field+"=1 and bounds='"+str(bounds)+"';"
    
    q=db.query(qry)
    ci=q.getresult()

    for i in range(len(ci)):
        cmass=ci[i][0].replace('{','').replace('}','').split(',')
        ret.append([(int(cmass[0]),int(cmass[1])),ci[i][5],ci[i][6],ci[i][7],ci[i][1],ci[i][2]])
        ci_id.append(ci[i][8])
        
    return ret,ci_id

# Update the CI column if a CI is detected 
def write_CI_Cmass(db,table,src,dtime,issue,lead,level,th,cmass,bounds,field):
    
    cmass=re.sub('[[(]','{',str(cmass))
    cmass=re.sub('[])]','}',cmass)
    
    qry="UPDATE "+table+" SET "+field+"=1 WHERE datetime='"+str(dtime)+"' and src='"+src+"' and issue="+str(issue)+" and lead="+str(lead)+\
        " and level="+str(level)+" and th="+str(th)+" and bounds='"+str(bounds)+"' and obj_cmass='{"+cmass+"}';"
    
    q=db.query(qry)
    
    return

# Update the ci_evol column after tracking
def write_CIevol_Cmass(db,table,src,dtime,issue,lead,level,th,cmass,bounds,field_plot,field_track,ci_id):
    
    cmass=re.sub('[[(]','{',str(cmass))
    cmass=re.sub('[])]','}',cmass)
    
    # First populate the evol fied (this is for plotting purposes)
    # There is a REDUNDANT FIELD for plotting [REMOVE LATER]
    qry="UPDATE "+table+" SET "+field_plot+"=1, "+field_track+"="+field_track+" || '{"+str(ci_id)+"}'"+\
        " WHERE datetime='"+str(dtime)+"' and src='"+src+"' and issue="+str(issue)+" and lead="+str(lead)+\
        " and level="+str(level)+" and th="+str(th)+" and bounds='"+str(bounds)+"' and obj_cmass='{"+cmass+"}';"

    q=db.query(qry)
    
    # Then populate the track fied (this is for plotting purposes)
    return
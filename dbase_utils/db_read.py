from pg import DB
import numpy as np


# Get Database Connection
def get_conn(hostname, username, password, dbname):
    db = DB(dbname=dbname, host=hostname, user=username, passwd=password)
    return db


# Read Object ij for a Single Object
def get_SingleObjij(db,table,src,dtime,issue,lead,level,th,objnum,bounds):
    
    qry="SELECT unnest(obj_ij) FROM "+table+" WHERE datetime='"+str(dtime)+"' and src='"+src+"' and issue="+str(issue)+" and lead="+str(lead)+\
        " and level="+str(level)+" and th="+str(th)+" and bounds='"+str(bounds)+"' and obj_num="+str(objnum)+";"
    
    q=db.query(qry)
    flat=q.getresult()
    obj_ij=np.asarray([flat[i]+flat[i+1] for i in range(0,len(flat),2)])
    
    return obj_ij

# Read Object ij for all the Objects in the Field
def get_AllObjij(db,table,src,dtime,issue,lead,level,th,bounds):
    
    qry="SELECT unnest(obj_ij) FROM "+table+" WHERE datetime='"+str(dtime)+"' and src='"+src+"' and issue="+str(issue)+" and lead="+str(lead)+\
        " and level="+str(level)+" and th="+str(th)+" and bounds='"+str(bounds)+"';"
    
    q=db.query(qry)
    flat=q.getresult()
    obj_ij=np.asarray([flat[i]+flat[i+1] for i in range(0,len(flat),2)])
    
    return obj_ij

# Read Single Object cmass
def get_SingleObjCmass(db,table,src,dtime,issue,lead,level,th,objnum,bounds):
    
    qry="SELECT unnest(obj_cmass) FROM "+table+" WHERE datetime='"+str(dtime)+"' and src='"+src+"' and issue="+str(issue)+" and lead="+str(lead)+\
        " and level="+str(level)+" and th="+str(th)+" and bounds='"+str(bounds)+"' and obj_num="+str(objnum)+";"
    
    q=db.query(qry)
    flat=q.getresult()
    obj_cmass=np.asarray([flat[i]+flat[i+1] for i in range(0,len(flat),2)])
    
    return obj_cmass

# Read Object cmass for all the Objects in the Field
def get_AllObjCmass(db,table,src,dtime,issue,lead,level,th,bounds):
    
    qry="SELECT unnest(obj_cmass) FROM "+table+" WHERE datetime='"+str(dtime)+"' and src='"+src+"' and issue="+str(issue)+" and lead="+str(lead)+\
        " and level="+str(level)+" and th="+str(th)+" and bounds='"+str(bounds)+"';"
    
    q=db.query(qry)
    flat=q.getresult()
    obj_cmass=np.asarray([flat[i]+flat[i+1] for i in range(0,len(flat),2)])
    
    return obj_cmass

def get_ObjCount(db,table,src,dtime,issue,lead,level,th,bounds):
    
    qry="SELECT distinct obj_num FROM "+table+" WHERE datetime='"+str(dtime)+"' and src='"+src+"' and issue="+str(issue)+" and lead="+str(lead)+\
        " and level="+str(level)+" and th="+str(th)+" and bounds='"+str(bounds)+"';"
    
    q=db.query(qry)
    objnums=q.getresult()
    
    return max(objnums)[0]

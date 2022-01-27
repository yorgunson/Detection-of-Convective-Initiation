import sys
sys.path.append('/mnt/user/soner.yorgun/utils')
import pgdb
from pg import DB
import itertools
import re
import numpy as np
import matplotlib.pyplot as plt
from prod_proj import ProdProj as pp

'''
lat1, lon1 = pp.map_xy(pp.ciws(),0,0,mkInt='round')
lat2, lon2 = pp.map_xy(pp.ciws(),5100,3500,mkInt='round')  

print lat1,lat2
print lon1,lon2
'''

lat1, lon1 = pp.map_xy(pp.hrrr(),0,0,mkInt='round')
lat2, lon2 = pp.map_xy(pp.hrrr(),1799,1059,mkInt='round')  

print lat1,lat2
print lon1,lon2

'''
def get_conn(hostname, username, password, dbname):
    conn = pgdb.connect(host=hostname, user=username, password=password, database=dbname)
    return conn

hostname='127.0.0.1'
database='object_soner'
username='nevsoper'
password=''
'''


'''
db = DB(dbname=database, host=hostname, user=username, passwd=password)
#conn = get_conn(hostname, username, password, database)

q=db.query("SELECT unnest(obj_ij) FROM object_repo WHERE datetime='2015-05-05 00:00:00' and obj_num=1;")
flat=q.getresult()
obj_ij=[flat[i]+flat[i+1] for i in range(0,len(flat),2)]
print obj_ij


hed=np.zeros((200,200))
zed=np.asarray(obj_ij)
print zed
hed[zed[:,0],zed[:,1]]=1

#for i in range(len(obj_ij)):
#    hed[obj_ij[i][0],obj_ij[i][1]]=1

plt.contourf(hed)
plt.show()
'''
'''
#db.query("INSERT INTO trial VALUES (8, ARRAY[[9,8],[11,13]]);")

q = db.query("SELECT array_length(obj_cmass,1) FROM trial WHERE objnum = 4;")
length=q.getresult()[0][0]
    
res=db.query("SELECT obj_cmass FROM trial WHERE objnum=6;")
cmasses=res.getresult()[0][0]
#print cmasses[1:-1]

#print re.match(r'\{(.*?)\}',cmasses[1:-1]).groups()

#ar=db.query("SELECT string_to_array(obj_cmass,',') FROM trial WHERE objnum=4;")


'''

'''
cur = conn.cursor()
cur.execute("SELECT current_database()")
dbname = cur.fetchone()[0]
print dbname
'''

'''
cur.execute("CREATE TABLE trial (objnum INTEGER PRIMARY KEY,obj_cmass INTEGER[]);")
conn.commit()
'''

'''
table='trial'
cur.execute("INSERT INTO " + table + " VALUES (6, ARRAY[[10,10],[11,13]]);")
conn.commit()


table='trial'
cur.execute("SELECT * FROM " + table + ";")
hed= cur.fetchall()

for i in range(len(hed)):
    print type(hed[i][0]),type(hed[i][1])
   

cur.execute("SELECT obj_cmass[2][2] FROM trial WHERE objnum=6;")
hzd= cur.fetchall()
print hzd

cur.execute("SELECT array_dims(obj_cmass) FROM trial WHERE objnum = 4;")
zed= cur.fetchall()
print type(zed)
''' 

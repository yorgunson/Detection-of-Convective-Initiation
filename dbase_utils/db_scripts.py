import pgdb
from pg import DB
import itertools

def get_conn(hostname, username, password, dbname):
#    conn = psycopg2.connect(host=hostname, user=username, password=password, database=dbname)
    conn = pgdb.connect(host=hostname, user=username, password=password, database=dbname)
    return conn

hostname='fvs-anb2'
database='object_soner'
username='nevsoper'
password=''

db = DB(dbname=database, host=hostname, user=username, passwd=password)

db.query("""CREATE TABLE object_repo_NE_sens (
            src varchar(10) NOT NULL,
            datetime timestamp NOT NULL,
            issue int,
            lead int,
            level int NOT NULL,
            obj_type varchar(80) NOT NULL,
            th real NOT NULL,
            bounds integer[] NOT NULL,
            obj_num int NOT NULL,
            obj_ij integer[] NOT NULL,
            obj_cmass integer[] NOT NULL,
            obj_area double precision NOT NULL,
            obj_mean double precision NOT NULL,
            obj_max double precision NOT NULL,
            info varchar(80) NULL,
            ci integer NULL,
            ci_15 integer NULL,
            ci_evol integer NULL,
            ci_evol_15 integer NULL,
            ci_track integer[] DEFAULT '{}',
            ci_track_15 integer[] DEFAULT '{}',
            id SERIAL NOT NULL,
            PRIMARY KEY(src,datetime,issue,lead,level,obj_num,th,bounds))""")


'''
db.query("""CREATE TABLE object_repo_regions_HRRR (
            src varchar(10) NOT NULL,
            datetime timestamp NOT NULL,
            issue int,
            lead int,
            level int NOT NULL,
            obj_type varchar(80) NOT NULL,
            th real NOT NULL,
            bounds integer[] NOT NULL,
            obj_num int NOT NULL,
            obj_ij integer[] NOT NULL,
            obj_cmass integer[] NOT NULL,
            obj_area double precision NOT NULL,
            obj_mean double precision NOT NULL,
            obj_max double precision NOT NULL,
            info varchar(80) NULL,
            ci_15 integer NULL,
            ci_evol_15 integer NULL,
            ci_track_15 integer[] DEFAULT '{}',
            id SERIAL NOT NULL,
            PRIMARY KEY(src,datetime,issue,lead,level,obj_num,th,bounds))""")
'''

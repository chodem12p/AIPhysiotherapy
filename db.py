import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey,select , inspect
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.schema import Table
from datetime import datetime
import uuid
import hashlib

import json

ip="localhost"
port="3306"
user="root"
password=""
database="fyp2"
engine = create_engine('mysql+pymysql://'+user+':'+password+'@'+ip+':'+port+'/'+database)
meta = MetaData()
conn = engine.connect()

userinfo = Table('userinfo', meta,autoload=True , autoload_with=engine)
notice = Table('notice', meta,autoload=True , autoload_with=engine)
sport = Table('sport', meta,autoload=True , autoload_with=engine)
userlog = Table('userlog', meta,autoload=True , autoload_with=engine)

session_factory = sessionmaker(bind=engine)
session = session_factory()


def istable(str):
    if str in ["userinfo", "notice", "sport", "userlog"]:
        return True
    return False


def insert(jsondict):
    """
    sql = "INSERT INTO "
    for table in jsondict["tables"]:
        sql+=table+","
    sql=sql[:-1]+" ("
    sql2=""
    for key,value in jsondict["columns"].items():
        sql+=key+","
        sql2+="'"+value+"',"
    sql=sql[:-1]+") VALUES (" +sql2[:-1]+")"
    print(sql,jsondict["columns"])
    """
    result = {}
    try:
        if istable(jsondict["tables"][0]):
            conn.execute(eval(jsondict["tables"][0]).insert().values(**jsondict["columns"]))
            result['status'] = "success"
    except:
        result['status'] = "fail"
        result['err'] = "重複userID"
    return result


def update(jsondict):
    result = {}
    try:
        if istable(jsondict["tables"][0]):
            conn.execute(eval(jsondict["tables"][0]).update().filter_by(**jsondict["where"]).values(**jsondict["update"]))
            result['status'] = "success"
    except:
        result['status'] = "fail"
        result['err'] = "不明原因"
    return result


def select(jsondict):
    result = {}
    result["select"] = []
    try:
        if istable(jsondict["tables"][0]):
            table = eval(jsondict["tables"][0])
            for a in conn.execute(table.select().filter_by(**jsondict["where"]).order_by(*jsondict["order"].keys())).fetchall():
                c = {}
                for i in range(len(table.columns.keys())):
                    c[table.columns.keys()[i]] = a[i]
                result["select"].append(c)
            result['status'] = "success"
    except:
        result['status'] = "fail"
        result['err'] = "不明原因"
    return result

def delete(jsondict):
    result = {}
    result["select"] = []
    try:
        conn.execute(notice.delete().filter_by(**jsondict["where"]))
        result['status'] = "success"
    except:
        result['status'] = "fail"
        result['err'] = "不明原因"
    return result

def selectlog(jsondict):
    result = {}
    result["select"] = []
    try:
        for row in conn.execute("SELECT * FROM userlog where userID = '"+jsondict["where"]["userID"]+"' and startdate BETWEEN  '"+jsondict["where"]["start"]+"' AND '"+jsondict["where"]["end"]+"' and enddate IS NOT NULL"):
            #print(row)
            result["select"].append({"date":row[3].strftime('%d-%m-%Y'),"start":row[3].strftime('%H:%M:%S'),"end":row[4].strftime('%H:%M:%S'),"sportName":row[2]})
        result['status'] = "success"
    except:
        result['status'] = "fail"
        result['err'] = "不明原因"
    return result


def datetime2str(datetime):
    #print(datetime.strptime(datetime, "%d %B, %Y"))
    return datetime.strftime("%d-%m-%Y, %H:%M:%S")

def dbcontrol(jdict,jsonstr=True):
    if jsonstr:
        jdict = json.loads(str(jdict))
    result={'status' : "fail",'err' : "不符合格式"}
    if jdict["method"] == "insert":
        print("insert")
        result = insert(jdict)
    elif jdict["method"] == "update":
        print("update")
        result = update(jdict)
    elif jdict["method"] == "select":
        print("select")
        result = select(jdict)
    elif jdict["method"] == "delete":
        print("delete")
        result = delete(jdict)
    elif jdict["method"] == "selectlog":
        print("selectlog")
        result = selectlog(jdict)
    if jsonstr:
        return json.dumps(result,default=datetime2str)
    return result


def checkAndCreateUser(userid: str, ack: str):  # return  0:錯誤(重復KEY) 1:正常 2:新建,ack
    req = {
        "method": "select",
        "tables": ["userinfo"],
        "where": {"userID": userid, "ack": ack},
        "order": {}
    }
    if len(dbcontrol(req, False)["select"]):
        return userid,ack  # 正常
    for i in range(20):
        inheritCode = hashlib.md5(userid.encode('utf-8')).hexdigest()
        ack = hashlib.md5((inheritCode + "12").encode('utf-8')).hexdigest()
        req = {
            "method": "insert",
            "tables": ["userinfo"],
            "columns": {"userID": userid, "ack": ack,"inheritCode":inheritCode}
        }
        if dbcontrol(req, False)["status"] == 'success':
            return userid,ack
        userid+=str(i)
    return "0","0"

#checkAndCreateUser("abcc", "000")

if __name__ == "__main__":
    # select
    req = {
        "method": "select",
        "tables": ["userinfo"],
        "where": {"userID": "userid", "ack": "ack"},
        "order": {}
    }
    # update
    req = {
        "method": "update",
        "tables": ["userinfo"],
        "columns": {"userID": "ccaaddccA", "ack": "99999"},
        "where": {"userID": "1123"},
        "update": {"inheritCode": "bbbbff"}
    }
    #insert
    req = {
        "method": "insert",
        "tables": ["userinfo"],
        "columns": {"userID": "55dd6", "ack": "ackabc"}
    }
    #del
    req = {
        "method": "delete",
        "where": {"userID": "userid", "sportname": "name"}
    };
    jsonstr = json.dumps(req)
    dbcontrol(jsonstr)
    dbcontrol(req,False)

    req = {
        "method": "selectlog",
        "where": {"userID": '5e364454048b8b039629a49a6e090795', "start": '2022-4-9', "end": '2022-4-20'},
    }

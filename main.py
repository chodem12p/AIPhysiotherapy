from ast import Str
from datetime import date
from pathlib import Path
from urllib import request
from fastapi import FastAPI, Form , Cookie
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from h11 import Data
from fastapi.responses import JSONResponse
from starlette.requests import Request
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from starlette.responses import HTMLResponse
from starlette.websockets import WebSocket
from torch import ne
import uvicorn
from typing import Optional
from datetime import datetime

import numpy as np
import cv2
import base64
from utils import *
from physiotherapy import *
from db import *
import mediapipe as mp
import time
import json


#from backend.routes.user import users

# from backend.routes.user import *
# from backend.routes.sport import *
# from backend.routes.log import *
# #test
# import FakeDatabase as Database
# import Myfunctions



app = FastAPI()

app.mount("/images", StaticFiles(directory="images"), name="images")
app.mount("/js", StaticFiles(directory="js"), name="js")
app.mount("/css", StaticFiles(directory="css"), name="css")
app.mount("/pwa", StaticFiles(directory="pwa"), name="pwa")

templates = Jinja2Templates(directory="html")

mpDraw = mp.solutions.drawing_utils
mpPose = mp.solutions.pose
pose = mpPose.Pose()





@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        jsondict = json.loads(str(data))

        jsondict = await AIsuggeut(jsondict)
        #print(jsondict)
        await websocket.send_text(json.dumps(jsondict))
@app.get("/") # 指定 api 路徑 (get方法)
def indexPage(request: Request):
    print("9999")
    return templates.TemplateResponse("relocation.html", {"request": request,})

@app.get("/index") # 指定 api 路徑 (get方法)
def indexPage(request: Request,userid :Optional[str] = Cookie(None),ack :Optional[str] = Cookie(None)):
    if not userid:
        mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
        userid = hashlib.md5(mac.encode('utf-8')).hexdigest()
        ack =""
        print("userid,mac",userid,ack)
    userid,ack = checkAndCreateUser(userid,ack)
    print("000")
    req = {"method": "select", "tables": ["userinfo"], "where": {"userID": userid}, "order": {}}
    dbreuslt = dbcontrol(req, False)
    weekNotice = dbreuslt["select"][0]["weekNotice"]
    print("abaafasf")
    response = templates.TemplateResponse("index.html", {"request": request,"weekNotice":weekNotice})
    response.set_cookie("userid", userid )
    response.set_cookie("ack",ack )
    return response



@app.post('/db')
@app.get("/db")
def creditPage(request: Request,jsonstr: str):
    aaaaa=(dbcontrol(jsonstr))
    #print(aaaaa)
    #print(type(aaaaa))
    return (aaaaa)

@app.get("/test")
def creditPage(request: Request,userid :Optional[str] = Cookie(None),ack :Optional[str] = Cookie(None)):
    if not userid:
        mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
        userid = hashlib.md5(mac.encode('utf-8')).hexdigest()
        ack =""
        print("userid,mac",userid,ack)
    userid,ack = checkAndCreateUser(userid,ack)


    response = templates.TemplateResponse("test.html", {"request": request})
    response.set_cookie("userid", userid )
    response.set_cookie("ack",ack )
    return response

@app.get("/test")
def creditPage(request: Request,userid :Optional[str] = Cookie(None),ack :Optional[str] = Cookie(None)):
    if not userid:
        mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
        userid = hashlib.md5(mac.encode('utf-8')).hexdigest()
        ack =""
        print("userid,mac",userid,ack)
    userid,ack = checkAndCreateUser(userid,ack)


    response = templates.TemplateResponse("test.html", {"request": request})
    response.set_cookie("userid", userid )
    response.set_cookie("ack",ack )
    return response

@app.get("/credit")
def creditPage(request: Request):
    return templates.TemplateResponse("credit.html", {"request": request})

@app.get("/tutorial")
def tutorialPage(request: Request,userid :Optional[str] = Cookie(None),ack :Optional[str] = Cookie(None)):
    if not userid:
        mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
        userid = hashlib.md5(mac.encode('utf-8')).hexdigest()
        ack =""
        print("userid,mac",userid,ack)
    userid,ack = checkAndCreateUser(userid,ack)


    response = templates.TemplateResponse("tutorial.html", {"request": request})
    response.set_cookie("userid", userid )
    response.set_cookie("ack",ack )
    return response

@app.get("/allCourse")
@app.get("/allCourse/{user_id}")
def allCoursePag(request: Request,userid :Optional[str] = Cookie(None),ack :Optional[str] = Cookie(None)):
    if not userid:
        mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
        userid = hashlib.md5(mac.encode('utf-8')).hexdigest()
        ack =""
        print("userid,mac",userid,ack)
    userid,ack = checkAndCreateUser(userid,ack)

    #couserInfo = fetch_sport()
    req = {"method": "select","tables": ["sport"],"where": {},"order": {} }
    dbreuslt=dbcontrol(req, False)
    if dbreuslt["status"]=="success":
        couserInfo = dbreuslt["select"]


    response = templates.TemplateResponse("allCourse.html", {"request": request,"couserInfos":couserInfo})
    response.set_cookie("userid", userid )
    response.set_cookie("ack",ack )
    return response

@app.get("/mySchedule")
@app.get("/mySchedule/{user_id}")
def mySchedulePage(request: Request,userid :Optional[str] = Cookie(None),ack :Optional[str] = Cookie(None)):
    if not userid:
        mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
        userid = hashlib.md5(mac.encode('utf-8')).hexdigest()
        ack =""
        print("userid,mac",userid,ack)
    userid,ack = checkAndCreateUser(userid,ack)

    req = {"method": "select", "tables": ["sport"], "where": {}, "order": {}}
    dbreuslt = dbcontrol(req, False)
    if dbreuslt["status"] == "success":
        couserInfo = dbreuslt["select"]
    #Schedules = Database.mySchedule
    req = {"method": "select", "tables": ["userinfo"], "where": {"userID": userid}, "order": {}}
    dbreuslt = dbcontrol(req, False)
    weekNotice = dbreuslt["select"][0]["weekNotice"]


    response = templates.TemplateResponse("mySchedule.html", {"request": request,"couserInfos":couserInfo,"weekNotice":weekNotice})
    response.set_cookie("userid", userid )
    response.set_cookie("ack",ack )
    return response

@app.get("/training/{sportname}")
def trainingPage(request: Request, sportname:str, userid:Optional[str] = Cookie(None), ack: Optional[str] = Cookie(None)):
    if not userid:
        mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
        userid = hashlib.md5(mac.encode('utf-8')).hexdigest()
        ack = ""
        print("userid,mac", userid, ack)
    userid, ack = checkAndCreateUser(userid, ack)

    response = templates.TemplateResponse("training.html", {"request": request,"sportname":sportname,"userid":userid})
    response.set_cookie("userid", userid)
    response.set_cookie("ack", ack)
    return response



#@app.get("/myRecord")
#@app.get("/myRecord/{user_id}")
#def logPage(request: Request,user_id: Optional[int]= None):
  #  return templates.TemplateResponse("myRecord.html", {"request": request})


@app.get("/myRecord")
@app.get("/myRecord/{user_id}")
def myRecord(request: Request, userid:Optional[str] = Cookie(None), ack: Optional[str] = Cookie(None)):
    if not userid:
        mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
        userid = hashlib.md5(mac.encode('utf-8')).hexdigest()
        ack = ""
        print("userid,mac", userid, ack)
    userid, ack = checkAndCreateUser(userid, ack)

    # req = {"method": "select", "tables": ["userlog"], "where": {"userID":userid}, "order": {"startdate":"DESC"}}
    # dbreuslt = dbcontrol(req, False)
    # if dbreuslt["status"] == "success":
    #     logs = dbreuslt["select"]


    response = templates.TemplateResponse("myRecord.html", {"request": request})
    response.set_cookie("userid", userid)
    response.set_cookie("ack", ack)
    return response


# @app.post("/myRecord")
# def allFill(request: Request,type:str = Form(...),date:str = Form(...)):
#     logs = Database.logs
#     logs = Myfunctions.getlogFromUser("A",logs)
#     logs = Myfunctions.logFilter(type,date,logs)
#     return templates.TemplateResponse("myRecord.html", {"request": request, "logs":logs,"type":type,"date":date})
#





# @app.get("/searching")
# async def searching(request: Request, userid:Optional[str] = Cookie(None), ack: Optional[str] = Cookie(None)):
#     if not userid:
#         mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
#         userid = hashlib.md5(mac.encode('utf-8')).hexdigest()
#         ack = ""
#         print("userid,mac", userid, ack)
#     userid, ack = checkAndCreateUser(userid, ack)
#
#
#     sport = Database.Sports
#
#     response = templates.TemplateResponse("searching.html", {"request": request,"sports":sport})
#     response.set_cookie("userid", userid)
#     response.set_cookie("ack", ack)
#     return response

#
# @app.post("/searching" , response_class=HTMLResponse)
# async def searching1(request: Request,name:str = Form(...)):
#     sport = Database.Sports
#     date = Myfunctions.searchFilter(name,sport)
#     return templates.TemplateResponse("searching.html", {"request": request,"sports":date})
#
#

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=5000, log_level="info")

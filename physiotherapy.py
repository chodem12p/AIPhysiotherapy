import cv2
import mediapipe as mp
import time
import math

import math
from typing import List, Mapping, Optional, Tuple, Union

import cv2
import dataclasses
import matplotlib.pyplot as plt
import numpy as np
import mediapipe as mp
from mediapipe.framework.formats import detection_pb2
from mediapipe.framework.formats import location_data_pb2
from mediapipe.framework.formats import landmark_pb2

from utils import *
from db import *

mpDraw = mp.solutions.drawing_utils
mpPose = mp.solutions.pose
pose = mpPose.Pose()

CUSTOMRDPOSE_CONNECTIONS = frozenset([(10, 12),(10, 9),(10, 11), (11, 13),
                              (13, 15), (15, 17), (15, 19), (15, 21), (17, 19),
                              (12, 14), (14, 16), (16, 18), (16, 20), (16, 22),
                              (18, 20), (11, 23), (12, 24), (23, 24), (23, 25),
                              (24, 26), (25, 27), (26, 28), (27, 29), (28, 30),
                              (29, 31), (30, 32), (27, 31), (28, 32)])

handlift_CONNECTIONS = frozenset([(10, 12),(10, 9),(10, 11), (11, 13),
                              (13, 15), (15, 17),
                              (12, 14), (14, 16), (16, 18),
                              (11, 23), (12, 24), (23, 24), (23, 25),
                              (24, 26), (25, 27), (26, 28), (27, 29), (28, 30),
                              (29, 31), (30, 32), (27, 31), (28, 32)])

legCoordination_CONNECTIONS = frozenset([(10, 12),(10, 9),(10, 11), (11, 13),
                              (13, 15), (15, 17), (15, 19), (15, 21), (17, 19),
                              (12, 14), (14, 16), (16, 18), (16, 20), (16, 22),
                              (18, 20), (11, 23), (12, 24), (23, 24), (23, 25),
                              (24, 26), (25, 27), (26, 28), (27, 29), (28, 30)])

def scalelen(pl1, a, b, size,sLength=None):
    if sLength:
        return math.hypot((pl1.landmark[a].x - pl1.landmark[b].x)*size[0], (pl1.landmark[a].y - pl1.landmark[b].y)*size[1])/sLength
    return math.hypot((pl1.landmark[a].x - pl1.landmark[b].x) * size[0],
                      (pl1.landmark[a].y - pl1.landmark[b].y) * size[1])

def newPoint(point,angle,bevel,size=None):
    radian = angle * math.pi / 180;
    if size:
        x, y = point[0]*size[0], point[1]*size[1]
        radian = angle * math.pi / 180;
        xMargin = math.cos(radian) * bevel;
        yMargin = math.sin(radian) * bevel;
        return ((x + xMargin)/size[0] , (y + yMargin)/size[1] )
    x, y = point[0], point[1]
    xMargin = math.cos(radian) * bevel;
    yMargin = math.sin(radian) * bevel;
    return (int(x + xMargin), int(y + yMargin))

def changepoint(pl,img,size,startIndex,target,anger,bevel,fixplace=None):
    copy = pl.landmark[target].x, pl.landmark[target].y
    pl.landmark[target].x, pl.landmark[target].y = newPoint((pl.landmark[startIndex].x, pl.landmark[startIndex].y), anger,
                                                     bevel, size)
    cv2.circle(img, (int(pl.landmark[target].x*size[0]), int(pl.landmark[target].y*size[1])), 5, (255, 0, 0), cv2.FILLED)
    fixx, fixy=  (pl.landmark[target].x-copy[0], pl.landmark[target].y-copy[1])
    #print(fixx, fixy)
    if fixplace:
        for i in fixplace:
            pl.landmark[i].x, pl.landmark[i].y = (pl.landmark[i].x+fixx, pl.landmark[i].y+fixy)


def findwangle(pl1,a, b):
    #BUG ang 180 can not test
        x1, y1 = pl1.landmark[a].x,pl1.landmark[a].y
        x2, y2 = pl1.landmark[b].x,pl1.landmark[b].y
        ang = 0
        if x1 == x2 and y1 > y2:
            ang = 0
        if (x2 > x1):
            ang = (math.atan2((x2 - x1), (y1 - y2)) * 180 / math.pi);
        elif ((x2 < x1)):
            ang = 360 - (math.atan2((x1 - x2), (y1 - y2)) * 180 / math.pi);
        elif ((x2 > x1) and (y2 <= y1)):
            ang = math.atan2(0, 0);
        #print(f"位置坐標 P1:{x1},{y1} P2:{x2},{y2}  角度:{(ang-90)%360}")
        return (ang-90)%360

def includedangle(p1, p2, p3):
    #夾角
    # Get the landmarks
    x1, y1 = p1.x , p1.y
    x2, y2 = p2.x , p2.y
    x3, y3 = p3.x , p3.y
    angle = math.degrees(math.atan2(y3 - y2, x3 - x2) - math.atan2(y1 - y2, x1 - x2))
    return angle + 360 if angle < 0 else angle

def checkfinish(pl,a,b,ang,range=10):
    nowang=int(findwangle(pl, a, b))
    #print("nowang"+str(nowang)+"  ang"+str(ang))
    if nowang <= ang +range and nowang >= ang -range :
        #print("Yes")
        return True
    #print("no")
    return False

def AIstep(pl,img,jsondict,ang=0):
    # pl: pose_landmarks
    # ang: 鏡頭 水平偏差修正數
    status=jsondict["status"]
    sportName=jsondict["sportName"]
    step=int(jsondict["step"])
    h, w, c = img.shape
    size= (w, h)

    #標準比例 12-11 (float)
    sLength=scalelen(pl,11,12,size)

    # print("-" * 10)
    testarray = [[12, 14, 0, 0],
                 [14, 16, 0, 0],
                 [16, 18, 0, 0],

                 [11, 13, 0, 0],
                 [13, 15, 0, 0],
                 [15, 17, 0, 0]]
    for i in testarray:
        i[2] = findwangle(pl, i[0], i[1])
        i[3] = scalelen(pl, i[0], i[1], size, sLength)
    print(testarray)

    print("**"*5)
    pl.landmark[9].x, pl.landmark[9].y=(pl.landmark[9].x+ pl.landmark[10].x)/2,(pl.landmark[9].y+ pl.landmark[10].y)/2
    pl.landmark[10].x, pl.landmark[10].y = (pl.landmark[11].x+ pl.landmark[12].x)/2,(pl.landmark[11].y+ pl.landmark[12].y)/2
    finish = True
    if sportName=="leglift":
        steparray = steps2array([2,1]*5+[2,3]*5+[2,"end"])
        if step in lange(steparray[1]):
            #左腳提高
            finish = checkfinish(pl,24,26,240) and finish
            changepoint(pl,img,size,24,26,240,(sLength*0.5285074470861518), [28,32,30])
            cv2.putText(img, "                  lift your right foot", (50, 50), cv2.FONT_HERSHEY_PLAIN, 3,
                (255, 0, 0), 3)
        elif step in lange(steparray[2]):
            #雙平地
            finish = checkfinish(pl, 24, 26, 120) and finish
            changepoint(pl,img,size,24,26,120,(sLength*0.4), [28,32,30])
            changepoint(pl,img, size, 23, 25, 70, (sLength * 0.4), [27, 29, 31])
            cv2.putText(img, "        put your foot down        ", (50, 50), cv2.FONT_HERSHEY_PLAIN, 3,(255, 0, 0), 3)
            pass
        elif step in lange(steparray[3]):
            #右腳提高
            finish = checkfinish(pl, 23, 25, 320) and finish
            changepoint(pl,img, size, 23, 25, 320, (sLength * 0.4), [27, 29, 31])
            cv2.putText(img, "lift your left foot", (50, 50), cv2.FONT_HERSHEY_PLAIN, 3,
                (255, 0, 0), 3)
            pass
        elif step in lange(steparray["end"]):
            jsondict["status"]="finish"
        else:
            cv2.putText(img, "Action finish", (50, 50), cv2.FONT_HERSHEY_PLAIN, 3,
                        (255, 0, 0), 3)
    elif sportName=="handlift":
        steparray = steps2array([1, 2, 3, 2, 1] * 5 + [4, 5, 6, 5, 4] * 5+["end"])

        if step in lange(steparray[1]):
            # 平地
            condition = [[12, 14, 98.17461846736921, 0.6902580599040706],
                         [14, 16, 84.93773727567952, 0.37773735201862757], ]
            for i in condition:
                finish = checkfinish(pl, i[0], i[1], i[2]) and finish
                changepoint(pl, img, size, i[0], i[1], i[2], (sLength * i[3]))
        elif step in lange(steparray[2]):
            # 半舉
            condition = [[12, 14, 113.96029247793061, 0.6378273472111569],
                         [14, 16, 276.4410411893788, 0.6224764965374783],
                         [16, 18, 282.46614821154986, 0.11619343025994516]]

            for i in condition:
                finish = checkfinish(pl, i[0], i[1], i[2]) and finish
                changepoint(pl, img, size, i[0], i[1], i[2], (sLength * i[3]))
            pass
        elif step in lange(steparray[3]):
            # 直舉
            condition = [[12, 14, 264.1618290034842, 0.7536999682464108],
                         [14, 16, 271.63608315393265, 0.7652743897135807],
                         [16, 18, 268.79541976125915, 0.16418990723144353]]

            for i in condition:
                finish = checkfinish(pl, i[0], i[1], i[2]) and finish
                changepoint(pl, img, size, i[0], i[1], i[2], (sLength * i[3]))
            pass
        elif step in lange(steparray[4]):
            # 直舉
            condition = [[11, 13, 84.24791703756054, 0.6849336992323491],
                         [13, 15, 97.854580023127, 0.3380177473595781]]

            for i in condition:
                finish = checkfinish(pl, i[0], i[1], i[2]) and finish
                changepoint(pl, img, size, i[0], i[1], i[2], (sLength * i[3]))
            pass
        elif step in lange(steparray[5]):
            # 直舉
            condition = [[11, 13, 72.41998500167762, 0.607371829473942],
                         [13, 15, 264.58002342016874, 0.750536024914535],
                         [15, 17, 256.44818754146416, 0.16598017953157682]]

            for i in condition:
                finish = checkfinish(pl, i[0], i[1], i[2]) and finish
                changepoint(pl, img, size, i[0], i[1], i[2], (sLength * i[3]))
            pass
        elif step in lange(steparray[6]):
            # 直舉
            condition = [[11, 13, 290.43324410749267, 0.6766797009239955],
                         [13, 15, 271.24600426337145, 0.757896269363437],
                         [15, 17, 274.113848616454, 0.2496786864110215]]
            for i in condition:
                finish = checkfinish(pl, i[0], i[1], i[2]) and finish
                changepoint(pl, img, size, i[0], i[1], i[2], (sLength * i[3]))
            pass
        elif step in lange(steparray["end"]):
            jsondict["status"]="finish"
        else:
            cv2.putText(img, "Action finish", (50, 50), cv2.FONT_HERSHEY_PLAIN, 3,
                        (255, 0, 0), 3)
            finish = False
    elif sportName=="legCoordination":
        steparray = steps2array( [1]+ [2, 3] * 5 + [1]+[5, 6] * 5+[1,"end"])

        if step in lange(steparray[1]):
            # 平地
            condition = [[24, 26, 124.98044236644037, 0.42459501378441455] ,
 [26, 28, 87.67749567590187, 1.3932282662443916] ,
 [28, 30, 73.8751143349717, 0.21399344486046792] ,
 [23, 25, 70.56650501941908, 0.38869783468525315] ,
 [25, 27, 93.81408799595565, 1.342737996233882] ,
 [27, 29, 107.92743951388687, 0.23024975504097367]]
            for i in condition:
                finish = checkfinish(pl, i[0], i[1], i[2],range=15) and finish
                changepoint(pl, img, size, i[0], i[1], i[2], (sLength * i[3]))
        elif step in lange(steparray[2]):
            # 左腳降低
            condition = [[24, 26, 127.83794496316324, 0.19523865763120393] ,
 [26, 28, 65.08652725144759, 1.313458504673499] ,
 [28, 30, 64.79011550152967, 0.14384624506425223]]


            for i in condition:
                finish = checkfinish(pl, i[0], i[1], i[2],range=15) and finish
                changepoint(pl, img, size, i[0], i[1], i[2], (sLength * i[3]))
            pass
        elif step in lange(steparray[3]):
            # 左腳提高
            condition = [[24, 26, 252.90255855262427, 0.45304677187760933] ,
 [26, 28, 74.49456199844408, 1.1394823798452804] ,
 [28, 30, 63.6923012220154, 0.12371225887922437] ]

            for i in condition:
                finish = checkfinish(pl, i[0], i[1], i[2],range=15) and finish
                changepoint(pl, img, size, i[0], i[1], i[2], (sLength * i[3]))
            pass
        elif step in lange(steparray[5]):
            # 右邊腳降低
            condition = [ [23, 25, 289.68212081904176, 0.43379758164247817] ,
 [25, 27, 112.35187854795825, 1.2359180598663662] ,
 [27, 29, 129.30766780385804, 0.12973258388232886]]
            for i in condition:
                finish = checkfinish(pl, i[0], i[1], i[2],range=15) and finish
                changepoint(pl, img, size, i[0], i[1], i[2], (sLength * i[3]))
            pass
        elif step in lange(steparray[6]):
            # 右邊腳提高
            condition = [[23, 25, 72.29567601856994, 0.2754341126485773] ,
 [25, 27, 111.2476625524061, 1.3671483249632603] ,
 [27, 29, 119.0500862823304, 0.16590503221990022]]

            for i in condition:
                finish = checkfinish(pl, i[0], i[1], i[2],range=15) and finish
                changepoint(pl, img, size, i[0], i[1], i[2], (sLength * i[3]))
            pass
        elif step in lange(steparray["end"]):
            jsondict["status"]="finish"
        else:
            cv2.putText(img, "Action finish", (50, 50), cv2.FONT_HERSHEY_PLAIN, 3,
                        (255, 0, 0), 3)
            finish = False
    if finish:
        jsondict["step"]=step+1

    print(str(finish)+" "+str(step)+" "+sportName+" "+status)
    return # jsondict,img

def lange(list):
    x=[]
    a=4 #3為格數
    for i in list:
        x+=[x for x in range(a*i,a*(i+1))]
    return x

def steps2array(index=[0, 1, 2, 1, 0]):
  arr={}
  step=0
  for i in set(index):
   arr[i]=[]
  for i in index:
    arr[i]+=[step]
    step+=1
  #print(arr)
  return arr

# async def AIsuggeut(jsondict,img=None):
async def AIsuggeut(jsondict, img=None):
    if img is None:
        img = base2cv(jsondict["image"])
    step = jsondict["step"]
    status = jsondict["status"]
    if status == "new":
        jsondict["startdate"]= datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        req = {
            "method": "insert",
            "tables": ["userlog"],
            "columns": {"userID": jsondict["userid"],"sportName": jsondict["sportName"],
                        "startdate":datetime.strptime(jsondict["startdate"], "%m/%d/%Y, %H:%M:%S")}
        }
        dbcontrol(req, False)
        jsondict["status"]="running"
        pass
    elif status == "finish":
        #修改DB完成時間
        jsondict = {
            "method": "update",
            "tables": ["userlog"],
            "where": {"userID": jsondict["userid"],"sportName": jsondict["sportName"],
                      "startdate": datetime.strptime(jsondict["startdate"], "%m/%d/%Y, %H:%M:%S")},
            "update": {"enddate": datetime.now()}
        }
        dbcontrol(jsondict, False)
        jsondict["status"] ="updated"
    pTime = time.time()
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = pose.process(imgRGB)

    if results.pose_landmarks:
        # h, w, c = img.shape size=(w, h)
        AIstep(results.pose_landmarks, img=img,jsondict=jsondict)
        #print(jsondict)
        if jsondict["sportName"]=="leglift":
            CONNECTIONS=CUSTOMRDPOSE_CONNECTIONS
        elif jsondict["sportName"]=="handlift":
            CONNECTIONS=handlift_CONNECTIONS
        else:
            CONNECTIONS=legCoordination_CONNECTIONS
        mpDraw.draw_landmarks(img, results.pose_landmarks, CONNECTIONS, landmark_drawing_spec=None)
        # for id, lm in enumerate(results.pose_landmarks.landmark):
        #     h, w, c = img.shape
        #     #print(id, lm)
        #     cx, cy = int(lm.x * w), int(lm.y * h)
        #     cv2.circle(img, (cx, cy), 5, (255, 0, 0), cv2.FILLED)

    cTime = time.time()+1
    fps = 1 / (cTime - pTime)
    cv2.putText(img, str(int(fps)), (70, 50), cv2.FONT_HERSHEY_PLAIN, 3,
                (255, 0, 0), 3)
    jsondict["image"] = opencv2jpeg(img)
    return jsondict

if __name__ == "__main__":
    cap = cv2.VideoCapture('PoseVideos2/PoseVideos2-1.mp4')
    jsondict={}
    jsondict["step"] = 1
    jsondict["status"] = "running"
    jsondict["sportName"] = "legCoordination"

    t = 0
    while t != -1:
        t += 1
        success, img = cap.read()
        jsondict,img = AIsuggeut(jsondict,img=img)

        cv2.imshow("Image", img)
        cv2.waitKey(0)

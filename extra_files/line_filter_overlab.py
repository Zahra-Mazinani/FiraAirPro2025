from djitellopy import Tello
from threading import Thread
import cv2
import time
import numpy as np
import math

mytello = Tello()
mytello.connect()

mytello.streamon()
time.sleep(2)

def nothing(x):
    pass

cv2.namedWindow("Tracking")
#making trackbar (horizontal slider)
cv2.createTrackbar('thr1 canny',"Tracking",100,500,nothing)
cv2.createTrackbar('thr2 canny',"Tracking",200,500,nothing)
cv2.createTrackbar('rho',"Tracking",1,255,nothing)
cv2.createTrackbar('thr1 hough',"Tracking",50,255,nothing)
cv2.createTrackbar('min line length',"Tracking",10,255,nothing)
cv2.createTrackbar('max line gap',"Tracking",15,255,nothing)

i=0
while True:
    frame = mytello.get_frame_read().frame
    frame = cv2.resize(frame,(0,0),fy=0.5,fx=0.5)

    blur = cv2.bilateralFilter(frame,9,75,75)

    cv2.imshow("bl",blur)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    thr1canny=cv2.getTrackbarPos('thr1 canny',"Tracking")
    thr2canny=cv2.getTrackbarPos('thr2 canny',"Tracking")
    rho=cv2.getTrackbarPos('rho',"Tracking")
    thr1hough=cv2.getTrackbarPos('thr1 hough',"Tracking")
    minline=cv2.getTrackbarPos('min line length',"Tracking")
    maxgap=cv2.getTrackbarPos('max line gap',"Tracking")

    l_bound = np.array([108,118,66])
    u_bound = np.array([142,255,203])

    mask = cv2.inRange(frame, l_bound, u_bound)

    dst = cv2.Canny(mask, 300, 500, None, 3)

    linesP = cv2.HoughLinesP(dst, rho, np.pi / 180, thr1hough, None, minline, maxgap)   
    LENS = []
    if linesP is not None:
        for i in range(0, len(linesP)):
            l = linesP[i][0]
            LEN  = math.sqrt((l[0]+l[2])+(l[1]+l[3]))
            LENS.append((LEN,l))
        # s=0
        # for i,j in LENS:
        #     if j > s :
        #         s =j
        if len(LENS)>=4:
            for i in range(4):
                l = LENS[i][1]
                cv2.line(frame, (l[0], l[1]), (l[2], l[3]), (0,0,255), 3, cv2.LINE_AA)

    cv2.imshow("mask",mask)
    cv2.imshow("frame", frame)
    i+=1

    # print("ofoghi_image_tello{}.png".format(i),frame)
    # cv2.imwrite("ofoghi_image_tello{}.png".format(i),frame)
    key = cv2.waitKey(20)
    if key == ord("q"):
        break

cv2.destroyAllWindows()
mytello.end()
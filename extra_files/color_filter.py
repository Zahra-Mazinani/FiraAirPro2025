from djitellopy import Tello
from threading import Thread
import cv2
import time
import numpy as np

mytello = Tello()
mytello.connect()

mytello.streamon()
time.sleep(2)

def nothing(x):
    pass

cv2.namedWindow("Tracking")
#making trackbar (horizontal slider)
cv2.createTrackbar('LH',"Tracking",0,255,nothing)
cv2.createTrackbar('LS',"Tracking",0,255,nothing)
cv2.createTrackbar('LV',"Tracking",0,255,nothing)
cv2.createTrackbar('UH',"Tracking",255,255,nothing)
cv2.createTrackbar('US',"Tracking",255,255,nothing)
cv2.createTrackbar('UV',"Tracking",255,255,nothing)
i=0
while True:
    frame = mytello.get_frame_read().frame
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)
    
    # clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    # frame[:, :, 2] = clahe.apply(frame[:, :, 2])
    lH=cv2.getTrackbarPos('LH',"Tracking")
    lS=cv2.getTrackbarPos('LS',"Tracking")
    lV=cv2.getTrackbarPos('LV',"Tracking")

    uH=cv2.getTrackbarPos('UH',"Tracking")
    uS=cv2.getTrackbarPos('US',"Tracking")
    uV=cv2.getTrackbarPos('UV',"Tracking")

    l_bound=np.array([lH,lS,lV])
    u_bound=np.array([uH,uS,uV])
    
    mask = cv2.inRange(frame, l_bound, u_bound)
    res =cv2.bitwise_and(frame,frame,mask=mask)
    # cv2.imshow("mask",mask)
    cv2.imshow("frame",res)
    i+=1
    # print("ofoghi_image_tello{}.png".format(i),frame)
    cv2.imwrite("ofo    ghi_image_tello{}.png".format(i),frame)
    key = cv2.waitKey(20)
    if key == ord("q"):
        break
cv2.destroyAllWindows()
mytello.end()
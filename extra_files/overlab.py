import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt

src = cv.imread("D:\\fira_air_2025\\codes\\extra_files\\imgs\\image_tello88.png")
# src = cv.imread("D:\\fira_air_2025\\codes\\extra_files\\imgs\\overlab\\overlabimage_tello286.png")

gate_lower_val = np.array([26,59,153])
gate_upper_val = np.array([82,208,255])

frame = cv.cvtColor(src, cv.COLOR_BGR2HSV)
# frame1 = cv.cvtColor(src, cv.COLOR_BGR2GRAY)

mask = cv.inRange(frame, gate_lower_val, gate_upper_val)

dst = cv.Canny(mask, 50, 200, None, 3)

linesP = cv.HoughLinesP(dst, 1, np.pi / 180, 50, None,250,300)

if linesP is not None:
    for i in range(0, len(linesP)):
        l = linesP[i][0]
        cv.line(src, (l[0], l[1]), (l[2], l[3]), (0,0,255), 3, cv.LINE_AA)
print(len(linesP))
cv.imshow("Detected Lines (in red) - Probabilistic Line Transform", src)

cv.imshow("",mask)
cv.waitKey()
cv.destroyAllWindows()
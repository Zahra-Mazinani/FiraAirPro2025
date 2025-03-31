from djitellopy import Tello
import cv2
import time
import numpy as np

mytello = Tello()
mytello.connect()
print(mytello.get_battery())

mytello.streamon()
time.sleep(2)

while True:
    frame = mytello.get_frame_read().frame
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2Lab)
    # اعمال Gaussian Blur برای حذف نویزها
    blurred_frame = cv2.GaussianBlur(hsv_frame, (7, 7), 1)

    # مقداردهی بازه رنگی (این مقادیر رو به دقت انتخاب کن)
    lower_val = np.array([0, 144, 49])
    upper_val = np.array([255, 255, 203])
        
    # ساخت ماسک
    mask = cv2.inRange(blurred_frame, lower_val, upper_val)

    # عملیات مورفولوژیکی برای حذف نویزها
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    
    label, lbl_img, stats, centroids = cv2.connectedComponentsWithStats(mask)
    
    if len(stats) > 1:  # چک کردن اینکه آیا حداقل یک جسم پیدا شده
        # پیدا کردن بزرگترین مساحت به جز پس‌زمینه (index 0)
        largest_index = np.argmax(stats[1:, cv2.CC_STAT_AREA]) + 1

        # گرفتن اطلاعات بزرگترین جسم
        x, y, w, h, area = stats[largest_index]
        # cx, cy = centroids[largest_index]
        cx = x+w//2
        cy = y+h//2
        # رسم مستطیل و مرکز
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
        cv2.circle(frame, (int(cx), int(cy)), 5, (0, 0, 255), -1)
        print(f"center: ({int(cx)}, {int(cy)})")
        input()
    else:
        print("no gate")
        
    # نمایش تصاویر
    cv2.imshow("Contours with Centers", frame)
    cv2.imshow("Mask", mask)
    if cv2.waitKey(1) & 0xFF == 27:  # کلید Esc برای خروج
        break

cv2.destroyAllWindows()
mytello.end()

from djitellopy import Tello
from threading import Thread
import cv2
import time
import numpy as np

mytello = Tello()
mytello.connect()

mytello.streamon()
time.sleep(2)


def calculate_brightness_contrast(pixels):
    """روشنایی (میانگین) و یک معیار ساده برای کنتراست (تفاوت min/max) را محاسبه می کند."""
    if not pixels:
        return 0, 0
    brightness = np.mean([np.mean(p) for p in pixels])
    min_val = np.min([np.min(p) for p in pixels])
    max_val = np.max([np.max(p) for p in pixels])
    contrast = max_val - min_val
    return brightness, contrast

def adjust_brightness_contrast(img, brightness_factor, contrast_factor):
    """روشنایی و کنتراست تصویر را تنظیم می کند."""
    adjusted_img = cv2.convertScaleAbs(img, alpha=contrast_factor, beta=brightness_factor)
    return adjusted_img

def filter_color_hsv(hsv_img, lower_bound_hsv, upper_bound_hsv):
    """فقط پیکسل هایی را نشان می دهد که در محدوده رنگ HSV مشخص شده قرار دارند."""
    # hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv_img, lower_bound_hsv, upper_bound_hsv)
    filtered_img = cv2.bitwise_and(img, img, mask=mask)
    return filtered_img

if __name__ == "__main__":
    while True:
        frame = mytello.get_frame_read().frame
        img = cv2.resize(frame,(0,0),fy=0.5,fx=0.5)

        # --- مرحله 2: تبدیل تصویر به فضای رنگی HSV ---
        hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        # --- مرحله 3: اعمال CLAHE بر روی کانال Value (V) ---
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        hsv_img_clahe = hsv_img.copy()
        hsv_img_clahe[:, :, 2] = clahe.apply(hsv_img[:, :, 2])

        # --- مرحله 4: تبدیل تصویر HSV CLAHE شده به BGR برای نمایش (اختیاری) ---
        img_clahe_bgr = cv2.cvtColor(hsv_img_clahe, cv2.COLOR_HSV2BGR)
        cv2.imshow('Image with CLAHE (HSV)', hsv_img_clahe)

        # --- مرحله 5: تعریف محدوده رنگ HSV برای فیلتر ---
        # شما باید بر اساس مقادیری که با کلیک روی تصویر بدست آوردید، این محدوده را تنظیم کنید.
        # lower_hsv = np.array([72,0,222])   # **مقادیر H، S، V پایین را تنظیم کنید**
        # upper_hsv = np.array([211,147,255])  # **مقادیر H، S، V بالا را تنظیم کنید**
        lower_hsv = np.array([108,62,177])
        upper_hsv = np.array([156,255,255])
        print(f"محدوده رنگ HSV برای فیلتر: پایین={lower_hsv}, بالا={upper_hsv}")

        # --- مرحله 6: فیلتر کردن رنگ در فضای HSV (بعد از اعمال CLAHE) ---
        filtered_hsv_image = filter_color_hsv(hsv_img_clahe, lower_hsv, upper_hsv)
        cv2.imshow('Color Filtered (HSV + CLAHE)', filtered_hsv_image)

        # --- مرحله 7: انتخاب پیکسل های نمونه برای روشنایی و کنتراست (از تصویر اصلی یا CLAHE شده) ---
        sample_pixels_coords =[(20,20), (180,130), (180, 20), (130,20)]  # می توانید این مختصات را تغییر دهید
        sample_pixels = [img_clahe_bgr[y, x] for x, y in sample_pixels_coords] # استفاده از تصویر CLAHE شده

        # --- مرحله 8: محاسبه میانگین روشنایی و کنتراست پیکسل های نمونه ---
        target_brightness, target_contrast = calculate_brightness_contrast(sample_pixels)
        print(f"روشنایی هدف: {target_brightness:.2f}, کنتراست هدف: {target_contrast:.2f}")

        # --- مرحله 9: محاسبه روشنایی و کنتراست فعلی تصویر (اختیاری - می توانید بر اساس نمونه ها تنظیم کنید) ---
        current_brightness, current_contrast = calculate_brightness_contrast([img_clahe_bgr])
        print(f"روشنایی فعلی (CLAHE): {current_brightness:.2f}, کنتراست فعلی (CLAHE): {current_contrast:.2f}")

        # --- مرحله 10: محاسبه ضرایب تنظیم روشنایی و کنتراست ---
        brightness_factor = target_brightness - current_brightness
        if current_contrast > 0:
            contrast_factor = target_contrast / current_contrast
        else:
            contrast_factor = 1.0
        print(f"ضریب روشنایی: {brightness_factor:.2f}, ضریب کنتراست: {contrast_factor:.2f}")

        # --- مرحله 11: اعمال تغییرات روشنایی و کنتراست روی تصویر فیلتر شده (در فضای BGR) ---
        # توجه: تنظیم روشنایی/کنتراست در اینجا بر روی تصویر BGR اعمال می شود.
        # اگر می خواهید آن را در فضای HSV اعمال کنید، باید تصویر فیلتر شده را به HSV برگردانید.
        adjusted_filtered_image = adjust_brightness_contrast(filtered_hsv_image, brightness_factor, contrast_factor)
        cv2.imshow('Color Filtered (HSV + CLAHE) and Adjusted', adjusted_filtered_image)

        # --- مرحله 12: نمایش تصویر اصلی برای مقایسه ---
        cv2.imshow('Original Image', img)

        if cv2.waitKey(5) & 0xFF == 27:
            break

    cv2.destroyAllWindows()
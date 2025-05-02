from config import *
from skyxel import *


# Initialize the Tello drone
drone = Tello()
drone.connect()
print("Battery : ", drone.get_battery())


drone.takeoff()
drone.move_up(60)


# Shared flag to terminate threads
stop_flag = threading.Event()

# Lock for accessing shared control information
control_info_lock = threading.Lock()

# Shared variables for control information
shared_gate_error = None
shared_line_cx = None
shared_line_senOut = None

# متغیر حالت برای کنترل رفتار
drone_state = "FOLLOWING_GATE"  # حالت اولیه: دنبال کردن گیت
line_follow_duration = 5  # مدت زمان دنبال کردن خط (به ثانیه)
line_follow_active = False
line_follow_start_time = 0

# line_controller
def sendCommands(senOut, cx):
    global curve
    ## TRANSLATION
    lr = (cx - width // 2) // senstivity
    lr = int(np.clip(lr, -10, 10))
    if 2 > lr > -2: lr = 0
    ## Rotation
    if   senOut == [1, 0, 0]: curve = weights[0]
    elif senOut == [1, 1, 0]: curve = weights[1]
    elif senOut == [0, 1, 0]: curve = weights[2]
    elif senOut == [0, 1, 1]: curve = weights[3]
    elif senOut == [0, 0, 1]: curve = weights[4]
    elif senOut == [0, 0, 0]: curve = weights[2]
    elif senOut == [1, 1, 1]: curve = weights[2]
    elif senOut == [1, 0, 1]: curve = weights[2]
    drone.send_rc_control(lr, fSpeed, 0, curve)


def control_drone():
    """کنترل پهپاد بر اساس اطلاعات اشتراکی."""
    global drone_state, line_follow_active, line_follow_start_time, shared_gate_error, shared_line_cx, shared_line_senOut

    with control_info_lock:
        gate_error = shared_gate_error
        line_cx = shared_line_cx
        line_senOut = shared_line_senOut

    if drone_state == "FOLLOWING_GATE":
        if gate_error is not None:
            error_x = gate_error[0] * kp_resize
            error_y = gate_error[1] * -kp_resize
            error_x = int(np.clip(error_x, -100, 100))
            error_y = int(np.clip(error_y, -100, 100))
            print(f"Control (Gate): X={error_x}, Y={error_y}")
            if abs(error_x) < threshold_x and abs(error_y) < threshold_y:
                print("Aligned. Moving forward through gate.")
                prev_time = time.time()
                while time.time() - prev_time < 0.5:
                    drone.send_rc_control(0, 40, 0, 0)
                drone.send_rc_control(0, 0, 0, 0)
            else:
                drone.send_rc_control(error_x, 10, error_y, 0)
        else:
            print("No gate error received.")
    elif drone_state == "FOLLOWING_LINE" and line_follow_active:
        if line_cx is not None and line_senOut is not None:
            sendCommands(line_senOut, line_cx)
        else:
            print("No line info received.")

    elif drone_state == "INITIATE_LINE_FOLLOWING" and not line_follow_active:
        print("Initiating line following sequence from control thread.")
        line_follow_active = True
        line_follow_start_time = time.time()
        print("=============== drone move down =================")
        max_attempts = 3
        for _ in range(max_attempts):
            try:
                h = drone.get_height()
                print("height", h)
                if h > 30:
                    # drone.move_down(20)
                    time.sleep(1)
                else:
                    drone_state = "FOLLOWING_LINE" # Transition to following line
                    break
            except:
                print("height error")
                drone_state = "FOLLOWING_GATE" # Go back to looking for gate on error
                break
        if drone_state == "INITIATE_LINE_FOLLOWING":
            drone_state = "FOLLOWING_LINE" # Ensure transition if loop completes

    if line_follow_active and drone_state == "FOLLOWING_LINE" and time.time() - line_follow_start_time >= line_follow_duration:
        print("Line following complete. ========== drone move up")
        # drone.move_up(20)
        time.sleep(1)
        line_follow_active = False
        drone_state = "FOLLOWING_GATE" # Go back to looking for gate

def stream_camera():
    """این تابع فریم را دریافت کرده، تشخیص گیت و خط را انجام می‌دهد و اطلاعات را در متغیرهای اشتراکی ذخیره می‌کند."""
    global drone_state, gate_not_detected_counter, shared_gate_error, shared_line_cx, shared_line_senOut
    gate_not_detected_counter = 0
    print("Attempting to start stream...")
    drone.streamon()

    print("Stream started successfully.")
    time.sleep(2)  # افزایش زمان انتظار برای اطمینان از برقراری استریم
    gate_not_detected_threshold = 10 # تعداد فریم هایی که گیت دیده نشده قبل از فعال شدن دنبال کردن خط
    while not stop_flag.is_set():
        frame = drone.get_frame_read().frame
        gate_error = None
        line_cx = None
        line_senOut = None
        if drone_state == "FOLLOWING_GATE":
            frame_processed_gate = preprocess(frame.copy())
            error, mask, frame_with_gate_detection = gate_center(frame_processed_gate)
            cv2.imshow("Gate Detection", frame_with_gate_detection)
            cv2.imshow("Gate mask", mask)
            gate_error = error
            if gate_error is not None:
                gate_not_detected_counter = 0
            else:
                gate_not_detected_counter += 1
                print(f"Gate not detected for {gate_not_detected_counter} frames.")
                if gate_not_detected_counter > gate_not_detected_threshold and not line_follow_active and drone_state == "FOLLOWING_GATE":
                    drone_state = "INITIATE_LINE_FOLLOWING"
                    gate_not_detected_counter = 0 # Reset counter
        elif drone_state == "FOLLOWING_LINE" and line_follow_active:
            img = cv2.resize(frame.copy(), (width, height))
            img_cropped = img[200:, 120:360]
            imgThres = thresholding_line(img_cropped)
            line_cx = getContours_line(imgThres, img_cropped)
            line_senOut = getSensorOutput(img_cropped, imgThres, sensors)
            cv2.imshow("Line Following", img_cropped)
            cv2.imshow("Line Path", imgThres)

        with control_info_lock:
            shared_gate_error = gate_error
            shared_line_cx = line_cx
            shared_line_senOut = line_senOut

        key = cv2.waitKey(1) & 0xFF
        if key == 27:
            stop_flag.set()
            break
        time.sleep(0.001)

def control_thread_loop():
    """ترد کنترل که اطلاعات را از متغیرهای اشتراکی خوانده و دستورات را ارسال می‌کند."""
    while not stop_flag.is_set():
        control_drone()
        time.sleep(0.001)

# Start the camera and controller threads
camera_thread = threading.Thread(target=stream_camera, daemon=True)
control_thread = threading.Thread(target=control_thread_loop, daemon=True)

camera_thread.start()
control_thread.start()

# Main loop to keep the program running
try:
    print(f"Battery: {drone.get_battery()}%")
    while True:
        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC key pressed
            print("Landing and stopping the program...")
            stop_flag.set()
            drone.land()
            break
except KeyboardInterrupt:
    print("Interrupted! Landing the drone...")
    stop_flag.set()
    drone.land()

# Wait for threads to finish
camera_thread.join()
control_thread.join()

drone.land()

# Safely disconnect the drone
drone.end()
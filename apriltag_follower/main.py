from config import *
from skyxel import *

# اتصال به پهپاد
drone.connect()
print("Battery : ", drone.get_battery())

# drone.takeoff()
# drone.move_up(60)

# پرچم توقف تردها
stop_flag = threading.Event()

# قفل برای دسترسی به متغیرهای مشترک
control_info_lock = threading.Lock()

# متغیرهای اشتراکی
shared_gate_error = None
shared_tag_position = None

# حالت کنترل
drone_state = "FOLLOWING_GATE"

# دیکشنری AprilTag
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
aruco_params = cv2.aruco.DetectorParameters()

def control_drone():
    """کنترل پهپاد بر اساس اطلاعات اشتراکی."""
    global drone_state, shared_gate_error, shared_tag_position

    with control_info_lock:
        gate_error = shared_gate_error
        tag_position = shared_tag_position

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

                # تغییر وضعیت به جستجوی تگ
                print("========= drone move down to search for AprilTag ==========")
                # drone.move_down(20)
                print("--------------DOWN----------------")

                time.sleep(1)
                drone_state = "SEARCHING_TAG"
            else:
                drone.send_rc_control(error_x, 10, error_y, 0)
        else:
            print("No gate error received.")

    elif drone_state == "SEARCHING_TAG":
        print("Searching for AprilTag...")
        if tag_position is not None:
            error_x = tag_position[0] * kp_resize
            error_y = tag_position[1] * -kp_resize
            error_x = int(np.clip(error_x, -100, 100))
            # error_y = int(np.clip(error_y, -100, 100))
            print(f"Aligning to AprilTag: X={error_x}, Y={error_y}")
            if abs(error_x) < threshold_x :   #and abs(error_y) < threshold_y:
                print("Aligned with AprilTag. Hovering.")
                drone.send_rc_control(0, 0, 0, 0)
                if ids[0] == 0 : 
                    drone.move_up(80)
                    drone.move_forward(20)
                    drone.move_down
            else:
                drone.send_rc_control(error_x, 0, error_y, 0)
        else:
            print("AprilTag not found. Going back up and looking for gate.")
            print("--------------UP----------------")
            # drone.move_up(20)
            time.sleep(1)
            drone_state = "FOLLOWING_GATE"

def stream_camera():
    """پردازش تصویر و استخراج اطلاعات موقعیت گیت و AprilTag."""
    global drone_state, shared_gate_error, shared_tag_position
    gate_not_detected_counter = 0
    gate_not_detected_threshold = 10

    print("Attempting to start stream...")
    drone.streamon()
    print("Stream started successfully.")
    time.sleep(2)

    while not stop_flag.is_set():
        frame = drone.get_frame_read().frame
        gate_error = None
        tag_position = None

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
                if gate_not_detected_counter > gate_not_detected_threshold:
                    gate_not_detected_counter = 0  # در این سناریو کار خاصی انجام نمی‌دیم

        elif drone_state == "SEARCHING_TAG":
            gray = cv2.cvtColor(frame.copy(), cv2.COLOR_BGR2GRAY)
            corners, ids, _ = cv2.aruco.detectMarkers(gray, aruco_dict, parameters=aruco_params)
            if ids is not None and len(ids) > 0:
                cx = int(np.mean(corners[0][0][:, 0]))
                cy = int(np.mean(corners[0][0][:, 1]))
                error_x = cx - width // 2
                error_y = cy - height // 2
                tag_position = (error_x, error_y)
                frame = cv2.aruco.drawDetectedMarkers(frame, corners, ids)
            cv2.imshow("AprilTag Detection", frame)

        with control_info_lock:
            shared_gate_error = gate_error
            shared_tag_position = tag_position

        key = cv2.waitKey(1) & 0xFF
        if key == 27:
            stop_flag.set()
            break
        time.sleep(0.001)

def control_thread_loop():
    while not stop_flag.is_set():
        control_drone()
        time.sleep(0.001)

# اجرای تردها
camera_thread = threading.Thread(target=stream_camera, daemon=True)
control_thread = threading.Thread(target=control_thread_loop, daemon=True)

camera_thread.start()
control_thread.start()

# حلقه اصلی
try:
    print(f"Battery: {drone.get_battery()}%")
    while True:
        key = cv2.waitKey(1) & 0xFF
        if key == 27:
            print("Landing and stopping the program...")
            stop_flag.set()
            drone.land()
            break
except KeyboardInterrupt:
    print("Interrupted! Landing the drone...")
    stop_flag.set()
    drone.land()

camera_thread.join()
control_thread.join()

drone.land()
drone.end()
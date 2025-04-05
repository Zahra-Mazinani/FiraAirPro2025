from config import *
from skyxel import *
import threading
import fake_tello

# Initialize the Tello drone
drone = fake_tello.FakeTello()
# drone = Tello()
drone.connect()
drone.takeoff()
drone.move_up(30)

# Shared flag to terminate threads
stop_flag = threading.Event()

# H detection files
H_template = cv2.imread(H_template_Path,0)
H_template = cv2.resize(H_template, (50, 50))  # Resize ROI to match template size

# متغیر اشتراکی برای ذخیره آخرین مقدار ارور
latest_error = None
error_lock = threading.Lock()

def stream_camera():
    """این تابع فریم را دریافت کرده و آخرین ارور را به‌روز می‌کند."""
    global latest_error

    drone.streamon()
    time.sleep(2)
    n = 0
    while not stop_flag.is_set():
        n+=1
        if n%5==1:
            frame = drone.get_frame_read().frame
            # found_H, (x, y, w, h) = H_detection(frame)
            frame,mask = preprocess(frame)
            error, frame = gate_center(frame,mask)
            # print(x, y, w, h)

            cv2.imshow("mask", mask)
            cv2.imshow("frame", frame)

            # ذخیره آخرین مقدار ارور
            with error_lock:
                latest_error = error

            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # If ESC key is pressed
                stop_flag.set()
                drone.land()
                break

def control(error):
    # os.system('cls')
    error_x = error[0]*-0.077
    error_y = error[1]*0.077
    error_x = int(np.clip(error_x,-100,100))
    error_y = int(np.clip(error_y,-100,100))
    print("\rX=====================================================")
    print("=====================================================")
    print("=====================================================")
    # error_x = pid_controller_x(x,0.077,0,0)
    # error_y = pid_controller_y(y,0.077,0,0)

    '''
    left_right_velocity: -100~100 (left/right)
    forward_backward_velocity: -100~100 (backward/forward)
    up_down_velocity: -100~100 (down/up)
    yaw_velocity: -100~100 (yaw)
    '''

    if abs(error_x) < threshold_x and abs(error_y)<threshold_y :
        prev_time = time.time()
        while time.time() - prev_time < 0.5:
            drone.send_rc_control(0,40,0,0)
            drone.send_rc_control(0,0,0,0)
            print("jellllllllllllllooooooooooooooooooooooooooooooo")

    else:
        print(error_x,error_y)
        drone.send_rc_control(error_x,5,error_y,0)

    print("=====================================================")
    print("=====================================================")
    print("=====================================================")

def control_loop():
    """این تابع ارور را خوانده و تابع کنترلر را اجرا می‌کند."""
    global latest_error

    while not stop_flag.is_set():
        with error_lock:
            if latest_error is not None:
                control(latest_error)

        time.sleep(0.05)  # تأخیر کوتاه برای جلوگیری از پردازش بی‌وقفه

# Start the camera and controller threads
camera_thread = threading.Thread(target=stream_camera, daemon=True)
control_thread = threading.Thread(target=control_loop, daemon=True)

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
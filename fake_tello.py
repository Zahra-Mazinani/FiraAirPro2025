# in the name of Allah
# for testing 

import cv2

class WebcamFrameReader:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            raise RuntimeError("Cannot open webcam")

    @property
    def frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return None
        # تبدیل به رزولوشن Tello (720x960)
        frame_resized = cv2.resize(frame, (960, 720))
        return frame_resized

    def release(self):
        self.cap.release()


class FakeTello:
    def __init__(self):
        print("[FakeTello] Created")
        self._frame_reader = WebcamFrameReader()

    def connect(self):
        print("[FakeTello] Connected to drone (simulated)")

    def takeoff(self):
        print("[FakeTello] Taking off... (simulated)")

    def land(self):
        print("[FakeTello] Landing... (simulated)")

    def send_rc_control(self, left_right, forward_backward, up_down, yaw):
        '''
        left_right_velocity: -100~100 (left/right)
        forward_backward_velocity: -100~100 (backward/forward)
        up_down_velocity: -100~100 (down/up)
        yaw_velocity: -100~100 (yaw)
        '''
        print(f"[FakeTello] Sending RC control - LR: {left_right}, FB: {forward_backward}, UD: {up_down}, YAW: {yaw}")

    def get_battery(self):
        print("[FakeTello] Getting battery level (simulated)")
        return 75

    def streamon(self):
        print("[FakeTello] Stream on (simulated)")

    def streamoff(self):
        print("[FakeTello] Stream off (simulated)")

    def get_frame_read(self):
        print("[FakeTello] Getting frame (from webcam)")
        return self._frame_reader

    def send_rc_control(self, left_right, forward_backward, up_down, yaw):
        print(f"[FakeTello] Sending RC command ({left_right}, {forward_backward},{up_down}, {yaw}")
    
    def move_up(self, x):
        print(f"[FakeTello] Moving up {x}cm (simulated)")

    def move_down(self, x):
        print(f"[FakeTello] Moving down {x}cm (simulated)")

    def end(self):
        print("[FakeTello] Releasing webcam (simulated)")
        self._frame_reader.release()

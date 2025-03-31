import djitellopy
import time

mytello = djitellopy.Tello()

mytello.connect()
print(mytello.get_battery())

mytello.takeoff()
time.sleep(2)
'''
    left_right_velocity: -100~100 (left/right)
    forward_backward_velocity: -100~100 (backward/forward)
    up_down_velocity: -100~100 (down/up)
    yaw_velocity: -100~100 (yaw)
'''
mytello.send_rc_control(0,-30,30,0)
time.sleep(2)
mytello.send_rc_control(0,0,0,0)

mytello.land()
mytello.end()
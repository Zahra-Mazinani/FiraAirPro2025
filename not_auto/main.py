import time
import cv2
import numpy as np
from djitellopy import Tello

class RobotController:
    def __init__(self, robot):
        self.robot = robot
        # Dictionary for manual control
        self.controls = {
            "forward_backward": 0,  # Move forward or backward (-100 to 100)
            "left_right": 0,        # Move left or right (-100 to 100)
            "up_down": 0,           # Move up or down (-100 to 100)
            "yaw": 0                # Rotate (-100 to 100)
        }

    def send_controls(self):
        """
        Sends control commands to the robot.
        """
        self.robot.send_rc_control(
            self.controls["left_right"],
            self.controls["forward_backward"],
            self.controls["up_down"],
            self.controls["yaw"]
        )

    def execute_command(self, command, duration):
        """
        Executes a single command for a specified duration.

        Args:
            command (dict): A dictionary containing control values.
            duration (float): The duration (in seconds) to execute the command.
        """
        self.controls.update(command)
        self.send_controls()
        start_time = time.time()  # Record the start time
        while time.time() - start_time < duration:
            self.send_controls()  # Continuously send the control commands
                # Reset controls to stop the robot after the command
        self.controls = {key: 0 for key in self.controls}
        self.send_controls()

if __name__ == "__main__":
    # Connect to the robot
    robot = Tello()
    robot.connect()

    print(f"Battery: {robot.get_battery()}%")  # Display battery level

    controller = RobotController(robot)

    # Define a sequence of commands with durations
    commands = [
        {"command": {"forward_backward": 50}, "duration": 0.5},  # Move forward for 2 seconds
        {"command": {"yaw": 30}, "duration": 0.5},            # Rotate for 1.5 seconds
        {"command": {"forward_backward": -50}, "duration": 0.5}, # Move backward for 2 seconds
        {"command": {"left_right": 50}, "duration": 0.5},       # Move right for 1 second
        {"command": {"left_right": -50}, "duration": 1},      # Move left for 1 second
        {"command": {"up_down": 50}, "duration": 1.5},        # Move up for 1.5 seconds
        {"command": {"up_down": -50}, "duration": 1.5},       # Move down for 1.5 seconds
    ]

    # Execute commands in sequence
    for item in commands:
        command = item["command"]
        duration = item["duration"]
        controller.execute_command(command, duration)

    # Land the robot after executing all commands
    robot.land()
    print("Robot landed.")
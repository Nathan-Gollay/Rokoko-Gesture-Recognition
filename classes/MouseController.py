"""
Object Used to run mouse control gestures

Author: Nathan Gollay
"""
# External Libraries
import time
import numpy as np
from pynput.mouse import Button, Controller
from scipy.spatial.transform import Rotation as R 

# Internal Files
from classes.StaticMovement import StaticMovement
from Compute.rotations import *

class MouseController:
    def __init__(self, skeleton, screen_x = 900.0, screen_y = 1440.0, load_pointer = False):
        self.skeleton = skeleton
        self.screen_x = screen_x
        self.screen_y = screen_y

        self.upper_left_quat = None
        self.upper_right_quat = None
        self.lower_left_quat = None
        self.lower_right_quat = None

        self.top_length = None
        self.bottom_length = None
        self.left_length = None
        self.right_length = None

        self.pointer_pose = None
        if load_pointer:
            self.loadPointerPose()
        else:
            self.setPointerPose()
        
    
    def getMousePosition(self):
        current_quat = quatToRotation(self.skeleton.getBoneRotations())[2]
        

        left_distance = quaternionAngleDifference(self.upper_left_quat, current_quat)
        right_distance = quaternionAngleDifference(self.lower_right_quat, current_quat)

        print("Left Distance: ", left_distance)
        print("Right Distance: ", right_distance)

        a = np.arccos((self.left_diagonal_length ** 2) + (left_distance ** 2) - (right_distance ** 2)/
                        (2 * self.left_diagonal_length * left_distance)) 
        
        print("\n\na: ", a)

        c = self.above_diagonal_angle - a

        print("c: ", c)

        vertical = (np.sin(c)/left_distance)
        horizontal = (np.cos(c)/right_distance)

        print("vertical: ", vertical)
        print("horizontal: ", horizontal)

        # Normalize to 0-1
        vertical_component = vertical/self.right_length
        horizontal_component = horizontal/self.top_length

        print("normal vertical: ", vertical_component)
        print("normal horizontal: ", horizontal_component)
        # Scale to screen size
        return horizontal_component * self.screen_x, vertical_component * self.screen_y

        
    def loadPointerPose(self):
        pass

    def setPointerPose(self):
        self.pointer_pose = StaticMovement(name = "pointer", load = False)
        self.pointer_pose.record(skeleton = self.skeleton, num_seconds = 3, fps = 30, 
            location = False, rotation = True, save = False)
        print(" Done Recording.\n")
    
    def calibrateMouse(self):
        pose = StaticMovement(name = "place_holder", load = False)
        print("\nPoint to the upper left corner")
        time.sleep(1)
        pose.record(skeleton = self.skeleton, num_seconds = 3, fps = 30, 
            location = False, rotation = True, save = False)
        print(" Done Recording.\n")
        pose.rotation_averages_quat = quaternionAverage(pose.rotations_array_quat)
        self.upper_left_quat = pose.rotation_averages_quat[2]

        print("\nPoint to the upper right corner")
        time.sleep(1)
        pose.record(skeleton = self.skeleton, num_seconds = 3, fps = 30, 
            location = False, rotation = True, save = False)
        print(" Done Recording.\n")
        pose.rotation_averages_quat = quaternionAverage(pose.rotations_array_quat)
        self.upper_right_quat = pose.rotation_averages_quat[2]

        print("\nPoint to the lower left corner")
        time.sleep(1)
        pose.record(skeleton = self.skeleton, num_seconds = 3, fps = 30, 
            location = False, rotation = True, save = False)
        print(" Done Recording.\n")
        pose.rotation_averages_quat = quaternionAverage(pose.rotations_array_quat)
        self.lower_left_quat = pose.rotation_averages_quat[2]

        print("\nPoint to the lower right corner")
        time.sleep(1)
        pose.record(skeleton = self.skeleton, num_seconds = 3, fps = 30, 
            location = False, rotation = True, save = False)
        print(" Done Recording.\n")
        pose.rotation_averages_quat = quaternionAverage(pose.rotations_array_quat)
        self.lower_right_quat = pose.rotation_averages_quat[2]

        self.calculateIntermediateValues()

        print("\nMouse Calibrated.")

    def calculateIntermediateValues(self):
        self.top_length = quaternionAngleDifference(self.upper_right_quat, self.upper_left_quat)
        self.bottom_length = quaternionAngleDifference(self.lower_right_quat, self.lower_left_quat)
        self.left_length = quaternionAngleDifference(self.upper_right_quat, self.lower_right_quat)
        self.right_length = quaternionAngleDifference(self.upper_left_quat, self.lower_left_quat)

        self.left_diagonal_length = quaternionAngleDifference(self.upper_left_quat, self.lower_right_quat)
        self.right_diagonal_length = quaternionAngleDifference(self.upper_right_quat, self.lower_left_quat)
        
        # For diagonal starting at left corner
        self.above_diagonal_angle = np.arccos(self.top_length/self.left_diagonal_length)

        print("\nTop Length: ", self.top_length)
        print("Bottom Length: ", self.bottom_length)
        print("Left Length: ", self.left_length)
        print("Right Length: ", self.right_length)

        print("\nRight Diagonal Length: ", self.right_diagonal_length)
        print("Left Diagonal Length: ", self.left_diagonal_length)
        print("Above Right Diagonal Angle: ", self.above_diagonal_angle)
import time
from scipy.spatial.transform import Rotation as R
import csv

from classes.Skeleton import Skeleton
from classes.StaticMovement import StaticMovement
from Compute.rotations import *

def determine_rotation_axis(skeleton):
    print("Put arm in leftmost position, facing screen")
    time.sleep(1)
    left_pose = StaticMovement(name = "left", load = False)
    left_pose.record(skeleton = skeleton, num_seconds = 3, fps = 30, location = False, rotation = True, save = False)
    #left_pose.record(skeleton = skeleton, num_seconds = 3, fps = 30, location = False, rotation = True, save = False)
    print("Done Recording")
    left_forearm_quat = quaternionAverage(left_pose.rotations_array_quat)[1]
    
    print("Put arm in rightmost position, facing screen")
    time.sleep(1)
    right_pose = StaticMovement(name = "right", load = False)
    right_pose.record(skeleton = skeleton, num_seconds = 3, fps = 30, location = False, rotation = True, save = False)
    print("Done Recording")
    right_forearm_quat = quaternionAverage(right_pose.rotations_array_quat)[1]

    quat_left_inv = left_forearm_quat.inv()
    axis_rotation = (quat_left_inv * right_forearm_quat)
    print(axis_rotation.as_quat())

    return left_forearm_quat, right_forearm_quat

def determineRotationAxis(skeleton, save = True):
    print("Put arm in left-most position, facing screen")
    time.sleep(1)
    left_pose = StaticMovement(name = "left", load = False)
    left_pose.record(skeleton = skeleton, num_seconds = 3, fps = 30, location = False, rotation = True, save = False)
    #left_pose.record(skeleton = skeleton, num_seconds = 3, fps = 30, location = False, rotation = True, save = False)
    print("Done Recording")
    left_forearm_quat = quaternionAverage(left_pose.rotations_array_quat)[1]
    
    print("Put arm in right-most position, facing screen")
    time.sleep(1)
    right_pose = StaticMovement(name = "right", load = False)
    right_pose.record(skeleton = skeleton, num_seconds = 3, fps = 30, location = False, rotation = True, save = False)
    print("Done Recording")
    right_forearm_quat = quaternionAverage(right_pose.rotations_array_quat)[1]

    quat_left_inv = left_forearm_quat.inv()
    axis_rotation = (quat_left_inv * right_forearm_quat)

    print("Put arm in top-most position, facing screen")
    time.sleep(1)
    left_pose = StaticMovement(name = "up", load = False)
    left_pose.record(skeleton = skeleton, num_seconds = 3, fps = 30, location = False, rotation = True, save = False)
    #left_pose.record(skeleton = skeleton, num_seconds = 3, fps = 30, location = False, rotation = True, save = False)
    print("Done Recording")
    up_forearm_quat = quaternionAverage(left_pose.rotations_array_quat)[1]
    
    print("Put arm in bottom-most position, facing screen")
    time.sleep(1)
    right_pose = StaticMovement(name = "down", load = False)
    right_pose.record(skeleton = skeleton, num_seconds = 3, fps = 30, location = False, rotation = True, save = False)
    print("Done Recording")
    down_forearm_quat = quaternionAverage(right_pose.rotations_array_quat)[1]

    quat_left_inv = left_forearm_quat.inv()
    axis_rotation = (quat_left_inv * right_forearm_quat)

    if save:
        saveCalibrationToCSV(left_forearm_quat, right_forearm_quat, up_forearm_quat, down_forearm_quat)

    return left_forearm_quat, right_forearm_quat, up_forearm_quat, down_forearm_quat

def saveCalibrationToCSV(left_end, right_end, up_end, down_end):
        write_path = "xy_calibration.csv"
        with open(write_path, 'w', newline='') as file:
            writer = csv.writer(file)
            
            writer.writerow(left_end.as_quat())
            writer.writerow(right_end.as_quat())
            writer.writerow(up_end.as_quat())
            writer.writerow(down_end.as_quat())

def loadCalibrationFromCSV():
    read_path = "xy_calibration.csv"
    quats = []
    with open(read_path, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            new_quat_row = []
            for quat in row:
                quat = quat.strip('[')
                quat = quat.strip(']')
                values = quat.split(' ')
                new_quat = []
                for val in values:
                    if val != '':
                        new_quat_row.append(float(val.strip(' ')))    
            quats.append(R.from_quat(new_quat_row))
    return quats[0], quats[1], quats[2], quats[3]

def projection_onto_axis(left_end, right_end, skeleton):
    try:
        current_quats = quatToRotation(skeleton.getBoneRotations())
    except:
        return 

    current_forearm_quat = current_quats[1]
    left_end_inv = left_end.inv()
    relative_rotation = left_end_inv * current_forearm_quat

    # Compute the angle of the relative rotation
    angle = quaternion_angle(relative_rotation)
    total_rotation_angle = quaternion_angle(left_end_inv * right_end)
    
    #relative_rotation = axis * forearm_quat
    #print(relative_rotation.as_quat())
    return angle/total_rotation_angle



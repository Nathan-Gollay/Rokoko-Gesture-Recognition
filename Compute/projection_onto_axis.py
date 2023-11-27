#def trackLeftRight()
import time
from scipy.spatial.transform import Rotation as R

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



"""
Functions to handle rotation math. Currently using quaternions
Author: Nathan Gollay
"""
# External Libraries
import numpy as np
from scipy.spatial.transform import Rotation as R
import math

def childRotationEuler(parent_old_euler, parent_new_euler, child_old_euler):
    # Calculates the rotation of the child node in correspondence with Parent movement.
    # ie, if the hand moves, where do the fingers move? 

    parent_old_rotation = R.from_euler('xyz', parent_old_euler)
    parent_new_rotation = R.from_euler('xyz', parent_new_euler)
    child_old_rotation = R.from_euler('xyz', child_old_euler)

    # Quaternion Calculation 
    parent_change = parent_new_rotation * parent_old_rotation.inv() # Formula for relative rotation
    child_new_rotation = parent_change * child_old_rotation # Apply Relative Rotation Matrix
    return child_new_rotation.as_euler('xyz') # Return as Euler (Radians)

def childRotationQuat(parent_old, parent_new, child_old):
    # Calculates the rotation of the child node in correspondence with Parent movement.
    # ie, if the hand moves, where do the fingers move? 
    parent_change = parent_new * parent_old.inv() # Formula for relative rotation
    child_new_rotation = parent_change * child_old # Apply Relative Rotation Matrix
    return child_new_rotation

def quaternionAngleDifference(quat_1, quat_2):
    # Function to calculate smallest rotation angle between two quats. Normalized to (0, pi). Returned in radians
    dq = quat_2 * quat_1.inv()
    angle1 = 2 * np.arccos(np.clip(dq.as_quat()[3], -1.0, 1.0))

    neg_quat_1 = R.from_quat(-(quat_1.as_quat()))
    #print (quat_1.as_quat(), quat_2.as_quat())
    # Calculate relative rotation from -quat_1 to quat_2
    dq_neg = quat_2 * (neg_quat_1).inv()
    angle2 = 2 * np.arccos(np.clip(dq_neg.as_quat()[3], -1.0, 1.0))

    # Return the smaller angle, ensuring it's within the range [0, pi]
    #print(quat_1.as_quat(), neg_quat_1.as_quat())
    return min(np.abs(angle1), np.abs(angle2))

def eulerToQuaternion(euler_array):
    # Takes flat array of euler rotations and returns quaternion array of shape (num_bones, 4) 
    num_bones = len(euler_array)//3
    euler_array = np.reshape(euler_array,(num_bones, 3)) 
    quaternions = R.from_euler('xyz', euler_array)
    return quaternions
def quatToRotationForRecord(quat_array):
    num_bones = len(quat_array)//4
    quat_array = np.reshape(quat_array,(num_bones, 4)) 
    #print (quat_array)
    quaternions = R.from_quat(quat_array)
    return quaternions

def quatToRotation(quat_array):
  
    quaternions = []
    quat = [0.0, 0.0, 0.0, 0.0]
    length = len(quat_array[:])/4
   
    for i in range(int(length)):
        quat[0] = quat_array[4 * i]
        quat[1] = quat_array[(4 * i) + 1]
        quat[2] = quat_array[(4 * i) + 2]
        quat[3] = quat_array[(4 * i) + 3]
        #print(quat)
        quaternions.append(R.from_quat(quat))
    return quaternions

def quaternionAverage(frames):
    # Determine the number of bones by looking at the first frame
    num_bones = len(frames[0])
    num_frames = len(frames)
    
    # Initialize a list to store the sum of quaternions for each bone
    quat_sums = [np.zeros(4) for _ in range(num_bones)]

    # Iterate through each frame
    for frame in frames:
        # Iterate through each bone's rotation
        for bone_index, rotation_obj in enumerate(frame):
            # Convert the rotation object to a quaternion (as an array)
            quat = rotation_obj.as_quat()
            
            # Ensure the quaternions are added in a consistent orientation
            if np.dot(quat_sums[bone_index], quat) < 0:
                quat = -quat
                
            quat_sums[bone_index] += quat

    # Normalize the summed quaternion for each bone to get the average quaternion
    average_rotations = [R.from_quat(quat_sum / np.linalg.norm(quat_sum)) for quat_sum in quat_sums]

    return average_rotations

def angleDifference(angle1, angle2):
    # Compute the difference
    difference = angle1 - angle2
    # Wrap the difference within the range -pi to pi
    difference = (difference + math.pi) % (2 * math.pi) - math.pi
    # If the difference is greater than pi, we take the 2*pi complement to find the shorter way around the circle
    if difference > math.pi:
        difference -= 2 * math.pi
    return difference
    
def determine_rotation_axis(quat_left, quat_right):
    quat_left_inv = quat_left.inv()
    axis_rotation = (quat_left_inv * quat_right_inv)
    return axis_rotation

def projection_onto_axis(axis, quat):
    relative_rotation = axis * quat
    return relative_rotation

def axisDistance(end_one, end_two, skeleton):
    try:
        current_quats = quatToRotation(skeleton.getBoneRotations())
    except:
        return 

    quat = current_quats[1]

    angle_diff_one = quaternionAngleDifference(end_one, quat)
    angle_diff_two = quaternionAngleDifference(end_two, quat)

    return angle_diff_one - angle_diff_two

def quaternion_angle(quat):
    quat = quat.as_quat()
    return 2 * np.arccos(quat[3])

def rotListToQuatList(rot_list):
    quat_list = []
    for rot in rot_list:
        quat_list.append(rot.as_quat())
    return np.concatenate(quat_list)


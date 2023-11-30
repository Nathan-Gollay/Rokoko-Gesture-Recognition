"""
Collection of Algorithms to detect static poses.

Author: Nathan Gollay
"""
#External Libraries
import math 
import numpy as np

#Internal Files
from classes.StaticMovement import *
from classes.Skeleton import *
from Compute.rotations import *

def metacarpalFingerDependencies(static_movement, skeleton):
    # Compares relation between metacarpals to average metacarpal relation of pose
    try:
        current_quats = quatToRotation(skeleton.getBoneRotations())
        #current_quats = np.array(rotListToQuatList(current_quats))
    except:
        return 
    
    relation_diff_total = 0.0
    k = 0
    for i, finger_one in enumerate(skeleton.finger_hierarchy_root.next_bones):
        for j, finger_two in enumerate(skeleton.finger_hierarchy_root.next_bones[i+1:]):
            finger_average_one = current_quats[finger_one.index]
            finger_average_two = current_quats[finger_two.index]
            relation = quaternionAngleDifference(finger_average_one, finger_average_two)
            relation_diff_total += abs(static_movement.metacarpal_average_relations[k] - relation)
            k += 1
    return relation_diff_total
            

def averageRotationComparison(static_movement, skeleton, return_total = False):
    # Simplest Case. Checks if each bone rotation is within a given threshold of
    # rotation from average of recording
    current_quats = None
    average_quats = None
    try:
        #print("calling from comparison: \n")
        current_quats = quatToRotation(skeleton.getBoneRotations())
        average_quats = static_movement.rotation_averages_quat
    except:
        print("wtf\n\n\n\n\n")
        return 100
    gesture = True
    i = 0
    if return_total:
        total = 0.0
        for i in range(len(current_quats) -3):
            curr = current_quats[i + 3]
            avg = average_quats[i + 3]
            i += 1
            diff_angle = quaternionAngleDifference(curr, avg)
            total += abs(diff_angle)
        return total

    for curr, avg in zip(current_quats[3:], average_quats[3:]):
        diff_angle = quaternionAngleDifference(curr, avg)
        if diff_angle > 0.35:
            #print(skeleton.bone_names[i])
            gesture = False
            #print(static_movement.skeleton.bone_names[i])
        i += 1
    if gesture:
        return True
        status = ("closed")
    else:
        return False
        status = "open"
    """
    if gesture: 
        return(static_movement.name)
    else:
         return(None)
    """

    #print(f'\rStatus: {status}', end='')
def euclideanDistance(array1, array2):
    total = 0.0
    for  elem_1, elem_2 in zip(array1, array2):
        diff = (elem_1 - elem_2) * (elem_1 - elem_2)
        total += diff
    return total


def nearestNeighbor(skeleton, class_average_quats):
    current_quat_array = quatToRotation(skeleton.getBoneRotations())
    min_distance = 100000
    min_letter_index = None

    i = 0
    for class_average in class_average_quats:
        #print(class_average)
        #print(rotListToQuatList(class_average))
        try:
            average_quats = np.array(rotListToQuatList(class_average))
        except:
            print("average")
            return 100, 'A'
            #print("averages: ", average_quats.shape)
        try:
            current_quats = np.array(rotListToQuatList(current_quat_array))
    
            #print("current: ", current_quats)
            #print("current: ", current_quats.shape)
        except:
            print("current")
            return 100, 'A'
        distance = euclideanDistance(average_quats, current_quats)
        if distance < min_distance:
            min_distance = distance
            min_letter_index = i
        i += 1
    return min_distance, min_letter_index

def angleAverageComparison(static_movement, skeleton, angle_averages):
    # Simple case. Compares average angle of hand to finger to current hand and finger angle
    # For use in non-localized roation data
    current_rotations = eulerToQuaternion(skeleton.getBoneRotations())
    static_movement.calculateAngleAverages()
    average_angles = angle_averages[3:]
    current_hand_quat = current_rotations[2]
    gesture = True
    #print(len(current_quats))
    #print(len(current_quats[3:]))
    #print(len(static_movement.rotation_averages_quat))
    #print(len(skeleton.bone_names))
    """
    for i, quat in enumerate(current_quats[3:]):
        
        #print(i)
        angle = quaternionAngleDifference(current_hand_quat, quat)
        average_angle = quaternionAngleDifference(static_movement.rotation_averages_quat[2], static_movement.rotation_averages_quat[i+3])
        #if angle < 0:
        #    angle = angle + (2 * np.pi)
       # if average_angle <  0:
         #   average_angle = average_angle + (2 * np.pi)

        #print("Bone Name: ", skeleton.bone_names[i+3])
        #print("Average Quat: ", static_movement.rotation_averages_quat[i].as_quat())
        #print("Current Quat: ", quat.as_quat())
        #print("Average Angle: ", average_angle)
        #print("Current Angle: ", angle, "\n")
        
        angle_difference = angleDifference(angle, average_angle)
        if abs(angle_difference) > 1.0:
            gesture = False
            print("\nBoneName: ",skeleton.bone_names[i+3] )
            print("Average Quat: ", static_movement.rotation_averages_quat[i].as_quat())
            print("Current Quat: ", quat.as_quat())
            print("Average Angle: ", average_angle)
            print("Current Angle: ", angle, "\n")
            #print (skeleton.bone_names[i+3])

         """   
    
    current_hand_rot = current_rotations[2]
    avg_hand_rot = static_movement.rotation_averages_quat[2]
    gesture = True

    for i, current_finger_rot in enumerate(current_rotations[3:], start=3):
        # Calculate the relationship (rotation) between average hand and average finger
        avg_finger_rot = static_movement.rotation_averages_quat[i]
        avg_relationship = avg_finger_rot * avg_hand_rot.inv()

        # Calculate the relationship (rotation) between current hand and current finger
        current_relationship = current_finger_rot * current_hand_rot.inv()

        # Calculate the difference between the two relationships
        relationship_diff = current_relationship * avg_relationship.inv()

        # Check if the difference is within acceptable bounds
        if relationship_diff.magnitude() > 2.0:
            gesture = False
            print("Bone Name: ", skeleton.bone_names[i])
            #print("Average Quat: ", static_movement.rotation_averages_quat[i].as_quat())
            #print("Current Quat: ", current_finger_rot.as_quat())
            #print("Average Angle: ", average_angle)
            #print("Current Angle: ", angle, "\n")
            #print("Magnitude Difference", relationship_diff.magnitude())
    
    if gesture:
        status = "closed"
    else:
        status = "open"
    print(f'\rStatus: {status}', end='')

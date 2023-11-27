"""
Class for recording, analyzing and copmuting on static movements
Examples of static movements: thumbs up, hand closed, etc

Author: Nathan Gollay
"""

# External Libraries
import time
import math 
import numpy as np
import csv
import re

# Internal Files
from Compute.rotations import *

class StaticMovement:
    def __init__(self, name, load = False, save = False, path = None):
        self.name = name
        self.frames = 0
        self.locations_array = []
        self.rotations_array = []
        self.location = False
        self.rotation = False
        self.hand_rotation = None
        self.skeleton = None
        
        self.rotations_array_quat = []

        self.hand_finger_angle_averages = None
        self.location_averages = None
        self.rotation_averages = None
        self.rotation_averages_quat = []

        self.metacarpal_average_relations = []

        self.save = save
        self.load = load
        self.recording_path = path

        if self.load:
            self.loadFromCSV(path)
       # self.location_min_array 
       # self.lcoation_max_array
       # self.rotation_min_array
       # self.rotation_max_array
    
    def saveToCSV(self, path):
        if path != None:
            write_path = path + '.csv'
        else:
            write_path = "Recordings/" + self.name + '.csv'
        with open(write_path, 'w', newline='') as file:
            writer = csv.writer(file)
            for frame in self.rotations_array_quat:
                writer.writerow(frame.as_quat())

    def loadFromCSV(self, path = None):
        read_path = None
        if self.recording_path != None:
            read_path = self.recording_path
        else:
            read_path = "Recordings/" + self.name + '.csv'
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
                            new_quat.append(float(val.strip(' ')))
                    new_quat_row.append(R.from_quat(new_quat))
                self.rotations_array_quat.append(new_quat_row)

            
    def eulerToQuaternion(self, flat_euler_array):
        # Takes euler array and converst to list of quaternions
        num_bones = len(euler_array)//3
        euler_array = np.reshape(flat_euler_array, (num_bones, 3))
        quaternions = R.from_euler('xyz', euler_array).as_quat()
        return quaternions

    def record(self, skeleton, num_seconds, fps, location = False, rotation = False, save = False, path = None):
        # Records Static Pose

        if not location and not rotation:
            raise Exception("at least one of location and rotation must be true")
        self.location = location
        self.rotation = rotation
        print("\nRecording...", end = "")
        start_time = time.time()
        sample_time = 1/fps
       
        self.rotations_array_quat = []
        while num_seconds >= time.time() - start_time:
            skip = False
            if location:
                self.locations_array.append(skeleton.getBoneLocations())
            if rotation:
                #otations_quaternion = eulerToQuaternion(skeleton.getBoneRotations())
                
                try:
                    #print(skeleton.getBoneRotations()[:])
                    rotations_quaternion = quatToRotationForRecord(skeleton.getBoneRotations())
                except:
                    skip = True
                    #print("skipped")
                    #print(rotations_quaternion)
                if not skip:
                    #print(rotations_quaternion.as_quat())
                    self.rotations_array_quat.append(rotations_quaternion)

            if not skip:
                self.frames+=1
                time.sleep(sample_time)
        
        if save:
            self.saveToCSV(path)
    
    def calculateAverages(self):
        # Calculates average values of recorded pose. 
        if self.rotation:
            raise Warning("Will only return euler average which is not always meaningful. Use quaternionAverage() instead")
        if self.frames == 0:
            raise Exception("No recorded frames")
        if not self.location and not self.rotation:
            raise Exception("Must record gesture before calulating")
        assert len(self.rotations_array) == len(self.locations_array)
        
        # Calculate location average array
        if self.location:
            self.location_averages = [0.0]*len(self.locations_array[0])
            for frame in self.locations_array:
                i = 0
                for element in frame[:]:
                    self.location_averages[i] = self.location_averages[i] + element
                    i += 1
            j = 0
            for entry in self.location_averages:
                self.location_averages[j] = entry/len(self.locations_array)
                j += 1
            
        #Calculate rotation average array
        if self.rotation:
            self.rotation_averages = [0.0]*len(self.rotations_array[0])
            for frame in self.rotations_array:
                i = 0
                for element in frame[:]:
                    self.rotation_averages[i] += element
                    i += 1
            j = 0
            for entry in self.rotation_averages:
                self.rotation_averages[j] = entry/len(self.rotations_array)
                j += 1

            self.hand_rotation = self.rotation_averages[6:9]
     
    def setMetacarpalDependencies(self, skeleton):
        # Sets metacarpal relations
        for i, finger_one in enumerate(skeleton.finger_hierarchy_root.next_bones):
            for j, finger_two in enumerate(skeleton.finger_hierarchy_root.next_bones[i+1:]):
                finger_average_one = self.rotation_averages_quat[finger_one.index]
                finger_average_two = self.rotation_averages_quat[finger_two.index]
                relation = quaternionAngleDifference(finger_average_one, finger_average_two)
                self.metacarpal_average_relations.append(relation)

    def locationIsolation(self, rotations):
        #Currently broken. Will modify infuture to isolate location instead
        rotation_change = [0.0, 0.0, 0.0]
        i = 0
        for average, current in zip(self.hand_rotation, rotations[6:9]):
         
            rotation_change[i] = average - current 
            i+=1
        i = 9
        for rotation in rotations[9:]:
            rotations[i] = rotation - rotation_change[i%3]
        return rotations

    def nearestNeighbor(self, skeleton):
        # Poor Approximation of nearest neighbor. Use only on location data

        raise Exception("Function not in working order. Refactor to handle location instead")
        self.skeleton = skeleton
        gesture = True
        current_rotations = skeleton.getBoneRotations()
        current_hand = current_rotations[6:9]

        new_finger_avgs = self.getHierarchicalAverages(current_hand)
                
        for finger in self.skeleton.finger_hierarchy_root.next_bones:
            finger = finger.next_bones.next_bones
            if abs(current_rotations[finger.index * 4] - new_finger_avgs[finger.index * 4]) > 0.5:
                gesture = False
        
        if gesture:
            status = "closed"
        else:
            status = "open"
        print(f'\rStatus: {status}', end='')
       
    def calculateAngleAverages(self):
        # Calculates angle between hand and finger. Only use for non local rotations
        self.hand_finger_angle_averages = [0.0] * len(self.rotation_averages_quat)
        for i, finger_quat in enumerate(self.rotation_averages_quat[3:]):
            self.hand_finger_angle_averages[i+3] = quaternionAngleDifference(self.rotation_averages_quat[2], finger_quat)
        #print("Hand to Finger Angles: ", self.hand_finger_angle_averages, "\n")

    def getHierarchicalAverages(self, current_hand_rotation, skeleton):
        # Takes new hand position (parent) and calulates recursively new rotation averages 
        # based on hierarchy.
        """
        In Current Development, not fully fucntional. Next Steps:
        1. Degree vs Radians
        2. Gimbal Lock- convert fully to quaternion
        3. Average Using quaternions!
        4. Also for checking in nearest neighbor
        5. Axis in correct order?
        """ 
        
        new_avgs = [None] * len(self.rotation_averages_quat)
        root = skeleton.finger_hierarchy_root

        for finger in root.next_bones:
            #print("\n\nHand Rotation Average", self.rotation_averages_quat[2].as_quat())
            #print("Hand Rotation Current", current_hand_rotation.as_quat())
            #print("Initial average rotation for finger index", skeleton.bone_names[finger.index], self.rotation_averages_quat[finger.index].as_quat())
            new_finger_rotation = childRotationQuat(self.rotation_averages_quat[2], 
                current_hand_rotation, 
                self.rotation_averages_quat[finger.index])
            new_avgs[finger.index] = new_finger_rotation
            #print("New rotation for finger index", skeleton.bone_names[finger.index], new_avgs[finger.index].as_quat())
            """   
            current_finger = finger
            while current_finger.next_bones != None:
                current_finger = current_finger.next_bones
                new_finger_rotation = childRotationQuat(self.rotation_averages_quat[2], 
                    current_hand_rotation, 
                    self.rotation_averages_quat[current_finger.index])
                new_avgs[current_finger.index] = new_finger_rotation

        
            """
            current_finger = finger
            while current_finger.next_bones != None:
                
                current_finger = current_finger.next_bones
                #print("Initial average rotation for bone index", skeleton.bone_names[current_finger.index], self.rotation_averages_quat[current_finger.index].as_quat())
                new_finger_rotation = childRotationQuat(self.rotation_averages_quat[current_finger.prev_bone.index],
                    new_avgs[current_finger.prev_bone.index], 
                    self.rotation_averages_quat[current_finger.index])
                new_avgs[current_finger.index] = new_finger_rotation
                #print("New rotation for bone index", skeleton.bone_names[current_finger.index], new_avgs[current_finger.index].as_quat())
        
        return new_avgs
        """
        #Uncomment for Euler Implementation, currently a bit broken I think
        new_avg_rotations = [0.0]*len(self.rotation_averages)
        for finger in self.skeleton.finger_hierarchy_root.next_bones:
            new_finger_vals = childRotation(self.hand_rotation, current_hand_rotation, 
                list([new_avg_rotations[finger.index * 3], new_avg_rotations[(finger.index * 3) + 1],
                new_avg_rotations[(finger.index * 3) + 2]]))

            new_avg_rotations[finger.index * 3] = new_finger_vals[0]
            new_avg_rotations[(finger.index * 3) + 1] = new_finger_vals[1]
            new_avg_rotations[(finger.index * 3) + 2] = new_finger_vals[2]

            current_finger = finger    

            while current_finger.next_bones != None:
                current_finger = current_finger.next_bones

                parent_finger_rotation_old = list([self.rotation_averages[current_finger.prev_bone.index * 3], 
                    self.rotation_averages[(current_finger.prev_bone.index * 3) + 1], 
                    self.rotation_averages[(current_finger.prev_bone.index * 3) + 2]])

                parent_finger_rotation_new = list([new_avg_rotations[current_finger.prev_bone.index * 3], 
                    new_avg_rotations[(current_finger.prev_bone.index * 3) + 1], 
                    new_avg_rotations[(current_finger.prev_bone.index * 3) + 2]])

                finger_rotation_old = list([self.rotation_averages[current_finger.index * 3], 
                    self.rotation_averages[(current_finger.index * 3) + 1],
                    self.rotation_averages[(current_finger.index * 3) + 2]])

                new_finger_vals = childRotation(parent_finger_rotation_old, parent_finger_rotation_new, finger_rotation_old)
               
                new_avg_rotations[current_finger.index * 3] = new_finger_vals[0]
                new_avg_rotations[(current_finger.index * 3) + 1] = new_finger_vals[1]
                new_avg_rotations[(current_finger.index * 3) + 2] = new_finger_vals[2]

        return new_avg_rotations
        """


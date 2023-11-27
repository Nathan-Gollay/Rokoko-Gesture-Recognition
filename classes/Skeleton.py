"""
Handles all things bone. Currently will break if use more than just right glove.
Easy refactor to change that

Author: Nathan Gollay
"""
# External Libraries
import time
from multiprocessing import Process, Value, Array, Lock 
from queue import *

#Internal Files
from classes.FingerNode import FingerNode


class Skeleton:
    # Class to handle all things bone related
    def __init__(self, pose, pipe):
        self.lock = Lock()
        self.pipe = pipe
        self.bone_names = None
        self.finger_hierarchy_root = FingerNode(None, None, None)

        self.bone_rotations_euler = Array('d', [0.0]*3*22) # 18 is number of bones (tech debt- magic number)
        self.bone_locations = Array('d', [0.0]*3*22) 
        
        self.num_bones = None
        self.ready = Value('i', 0)
        self.bone_rotations_quat = Array('d', [0.0] * 4 * 22)
    
    def setDimensions(self, pose):
        # Will be more neceessary as code becomes more robust (tech debt)
        self.num_bones = len(pose)
        self.bone_names = [""]*len(pose)
    
    def setFingerBoneGroups(self):
        # Sets hierarchical structure of bones in Tree. Slow. Only call once at beginning 

        self.finger_hierarchy_root.index = self.bone_names.index('RightHand') # Root is hand in this case
        self.finger_hierarchy_root.root = self.finger_hierarchy_root
        self.finger_hierarchy_root.next_bones = []
        
        # Create queue of finger bone names, realizing never actually needed a queue...oh well
        finger_bones = Queue()
        for finger in self.bone_names[3:]: # Currently fingers start at index 3
            finger_bones.put(finger)
    
        # Add each to appropriate place in tree
        while finger_bones.qsize() != 0:
            bone_name = finger_bones.get()
            finger_num = None
            if '1' in bone_name:
                finger_num = 1
            elif '2' in bone_name:
                finger_num = 2
            elif '3' in bone_name:
                finger_num = 3
            elif '4' in bone_name:
                finger_num = 4
            elif '5' in bone_name:
                finger_num = 5
            else: 
                raise Exception("Attempting to create finger bone structure from non-finger bone")
            
            # Metacarpal-> Proximal -> Medial ->Distal
            position = None
            if 'Metacarpal' in bone_name:
                position = 1
            elif 'Proximal' in bone_name:
                position = 2
            elif 'Medial' in bone_name:
                position = 3
            elif 'Distal' in bone_name:
                position = 4
            else: 
                raise Exception("Attempting to create finger bone structure from non-finger bone")
            
            new_finger = FingerNode(bone_name, position, finger_num)
            new_finger.root = self.finger_hierarchy_root
            new_finger.index = self.bone_names.index(new_finger.name) # Important: is how bone data accessed

            # Insert in Tree
            found = False
            for finger in self.finger_hierarchy_root.next_bones:
                
                if finger.finger_num == finger_num:
                    found = True
                    
                    current_node = finger
                    while new_finger.type > current_node.type and current_node.next_bones:
                        current_node = current_node.next_bones
                    current_node.insert(new_finger)
                    
            if not found:
                self.finger_hierarchy_root.next_bones.append(new_finger)
                new_finger.prev_bone = self.finger_hierarchy_root

    def printFingerGroups(self):
        # Function to print out bone hierearchies
        for finger in self.finger_hierarchy_root.next_bones:
            print ("RightHand-> ", end = " ")
            print(finger.name, end = " ")
            curr = finger
            while curr.next_bones:
                curr = curr.next_bones
                print("-> ", curr.name, end = " ")
            print("\n", end = " ")

    def getActiveBones(self):
        # Currently Obsolete in favor of similar fucniton in Blender Script
        # If Rokoko works will use this
        active_bones = []
        for i in range(5):
            time.sleep(1)
            new_pose = getPose()['parameters']
            for bone_prev, bone_new in zip(self.pose, new_pose):
                print(bone_prev)
                print(bone_new)
                if bone_prev != bone_new:
                    active_bones.append(bone_prev)
            self.pose = new_pose

    def printOut(self):
        # Currently obsolete. If Rokok API fixed, will be used
        print("\nPOSE DEFINITION:\n")
        print(self.pose_definition)

        print("\nPOSE:\n")
        print(self.pose)
    
    def getBoneLocations(self):
        with self.lock:
            return self.bone_locations
    
    def getBoneRotations(self):
        with self.lock:
            return self.bone_rotations_quat
    
    def isReady(self):
        # Should be used to make sure skeleton is ready
        with self.lock:
            return self.ready.value == 1

    def setReady(self, ready):
        # Needs Work/Refactor
        with self.lock:
            if ready:
                self.ready.value = 1
            else:
                self.ready.value = 0
   

    def updateWithRokoko(self, pose):
        with self.lock:
            for i in range(len(pose)): 
                if isinstance(pose[i], str):
                    return
                self.bone_rotations_quat[i] = pose[i]
            

    def update(self, pose_array):
        # Function to read values from Sample Process
        # If first data received
        if not self.num_bones: 
            # Should add more logic here. Like self.ready
            self.setDimensions(pose_array)
            i = 0
            for bone in pose_array:
                self.bone_names[i] = bone[0]
                i+= 1
            print("\nActive Bones: ", self.bone_names)
            self.pipe.send(self.bone_names) # Needs to be done because no shared memory for strings

        self.setReady(True) # Doesn't work, and probably needs to be locked
        assert len(pose_array) == self.num_bones
        with self.lock:
            # Actual Update
            i = 0
            for bone in pose_array:
                for axis in range(3):
                    self.bone_locations[(3*i)+ axis - 1] = bone[1][axis-1]
                    self.bone_rotations_euler[(3*i)+ axis -1] = bone[2][axis-1]
                i +=1
           


    


    
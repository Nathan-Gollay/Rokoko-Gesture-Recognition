"""
Class to handle sign language alphabet applications

Author: Nathan Gollay
"""

# External Libraries
import string
import os
import time
import multiprocessing as mp

# Internal Files
from classes.StaticMovement import StaticMovement
from classes.Skeleton import Skeleton
from classes.StaticMovement import StaticMovement
from Compute.rotations import *
from Compute.pose_detection_algorithms import *
from Compute.projection_onto_axis import *
from MouseAndKeyboard.keyboard import *

class SignLanguage:
    def __init__(self, unique_identifier, record_button_pushed, recording_name_conn, load = False, save = True):
        self.unique_identifier = unique_identifier
        self.load = load
        self.save = save
        self.record_button_pushed = record_button_pushed
        self.recording_name_conn = recording_name_conn

        self.lock = mp.Lock()
        self.pose_objects = []
        if self.load:
            self.load_recordings()
    
    def runAverageAngleComparison(self, skeleton, push_keys = False):
        alphabet = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I','K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y']
        dir_path = "./Sign_Language_Recordings/" + self.unique_identifier

        class_average_quats = []
        for pose in self.pose_objects:
            class_average_quats.append(pose.rotation_averages_quat)
            pose.setMetacarpalDependencies(skeleton)
            #print("deps: ", pose.metacarpal_average_relations)
        
        while True:
            if self.record_button_pushed.value == 1:
                print("button press received")
                file_name = None
                while file_name == None:
                    print("in while loop", flush = True)
                    file_name = self.recording_name_conn.recv()
                    
                print("recieved")
                file_path = dir_path + '/' + file_name
                new_letter_pose = StaticMovement(name = file_name[-1], load = False)
                new_letter_pose.record(skeleton = skeleton, num_seconds = 4, fps = 30, 
                    location = False, rotation = True, save = True, path = file_path)
                print(" Done Recording.\n")
                new_letter_pose.rotation_averages_quat = quaternionAverage(new_letter_pose.rotations_array_quat)
                new_letter_pose.calculateAngleAverages()
                new_letter_pose.setMetacarpalDependencies(skeleton)

                self.pose_objects[alphabet.index(file_name[-1])] = new_letter_pose
                class_average_quats[alphabet.index(file_name[-1])] = new_letter_pose.rotation_averages_quat
                with self.lock:
                    self.record_button_pushed.value = 0
                run = True
            
            #time.sleep(1)
            
            minimum = 100.0
            min_letter = None
            #print("\n")
            for i, pose in enumerate(self.pose_objects):
                total = averageRotationComparison(pose, skeleton, return_total = True)
                #relation_total = metacarpalFingerDependencies(pose, skeleton)
                #print(pose.name, ": ", total) 
                if total  <  minimum:
                    minimum =  total 
                    min_letter = pose.name
            
            if push_keys:
                if minimum < 1.5:
                    pushKey(min_letter)
                    time.sleep(.8)
                    
                 

    def runNearestNeighbor(self, skeleton):
        alphabet = string.ascii_uppercase
        dir_path = "./Sign_Language_Recordings/" + self.unique_identifier

        class_average_quats = []
        for pose in self.pose_objects:
            class_average_quats.append(pose.rotation_averages_quat)
        

        while True:
            if self.record_button_pushed.value == 1:
                print("button press received")
                file_name = None
                while file_name == None:
                    print("in while loop", flush = True)
                    file_name = self.recording_name_conn.recv()
                    
                print("recieved")
                file_path = dir_path + '/' + file_name
                new_letter_pose = StaticMovement(name = file_name[-1], load = False)
                new_letter_pose.record(skeleton = skeleton, num_seconds = 4, fps = 30, 
                    location = False, rotation = True, save = True, path = file_path)
                print(" Done Recording.\n")
                new_letter_pose.rotation_averages_quat = quaternionAverage(new_letter_pose.rotations_array_quat)
                #new_letter_pose.calculateAngleAverages()

                self.pose_objects[alphabet.index(file_name[-1])] = new_letter_pose
                class_average_quats[alphabet.index(file_name[-1])] = new_letter_pose.rotation_averages_quat
                with self.lock:
                    self.record_button_pushed.value = 0
                run = True
            
            time.sleep(0.5)
            distance, letter = nearestNeighbor(skeleton, class_average_quats)
            print(letter, distance)
            
            """
            minimum = 100
            min_letter = None
            
            for i, pose in enumerate(self.pose_objects):
                total = averageRotationComparison(pose, skeleton, return_total = True)
                if total < minimum:
                    minimum = total
                    min_letter = pose.name
            """
            """
            if minimum < 0.075:
                pushKey(min_letter)
                time.sleep(1)
            """               
    def loadRecordings(self, letters = string.ascii_uppercase):
        recording_path = "./Sign_Language_Recordings/" + self.unique_identifier
        if not os.path.exists(recording_path):
            raise Exception("Unique Identifier does not exist. Load or record another.")

        for letter in letters:
            path = recording_path + '/' + self.unique_identifier + '_' + letter + '.csv'
            letter_pose = StaticMovement(name = letter, load = True, path = path)

            letter_pose.rotation_averages_quat = quaternionAverage(letter_pose.rotations_array_quat)
            #letter_pose.calculateAngleAverages()
            self.pose_objects.append(letter_pose)


    def record(self, skeleton, letters = string.ascii_uppercase):
        recording_path = "./Sign_Language_Recordings/" + self.unique_identifier
        if not os.path.exists(recording_path):
            os.mkdir(recording_path)
        else:
            print("Provded Unique Identier is already in use. Will overwrite.")
            print("Exit program to avoid!")
        
        for letter in letters:
            letter_pose = StaticMovement(name = letter, load = False)
            print("When ready, press 'record' to record pose for: " + letter, flush = True)
            while self.record_button_pushed.value != 1:
                time.sleep(0.1)
            print("recieved")
            letter_pose.record(skeleton = skeleton, num_seconds = 3, fps = 30, location = False, 
                rotation = True, save = True, path = recording_path + '/' + self.unique_identifier)
            print(" Done Recording.\n")
            letter_pose.rotation_averages_quat = quaternionAverage(letter_pose.rotations_array_quat)
            letter_pose.calculateAngleAverages()
            
            self.pose_objects.append(letter_pose)

            with self.lock:
                self.record_button_pushed.value = 0
                




#example = SignLanguage("nate", load = False)
#example.record()

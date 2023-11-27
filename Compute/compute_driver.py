"""
Main computing driver. Separate Process from Sampling (blender_access) or main.

Author: Nathan Gollay
"""
# External Libraries
import time
import multiprocessing
import string

# Internal Files
from classes.Skeleton import Skeleton
from classes.StaticMovement import StaticMovement
from Compute.rotations import *
from Compute.pose_detection_algorithms import *
from Compute.projection_onto_axis import *
from classes.SignLanguage import SignLanguage
from classes.MouseController import MouseController

def computePROCESS(skeleton, child_conn, record_button_pushed, save_button_pushed, load_button_pushed, 
        pose_name_conn, identifier_conn, video_parent_conn, video_parent_conn_2, skeleton_ready, 
        shutdown, sensitivity_slider, recording_name_conn, bone_name_conn):
    # Main Compute Driver
    lock = multiprocessing.Lock()
    while skeleton_ready.value != 1:
        time.sleep(.1)
    
    while skeleton.bone_names == None:
        skeleton.bone_names = bone_name_conn.recv()

    skeleton.setFingerBoneGroups() # Done to create bone tree
    print("\nFinger Hierarchies:")
    skeleton.printFingerGroups() 
    alphabet = string.ascii_uppercase

    """
    mouse = MouseController(skeleton = skeleton)
    mouse.calibrateMouse()
    while True:
        print("\nNormalized: ",mouse.getMousePosition())
        time.sleep(.5)
    """
    signs = SignLanguage("Nathan", record_button_pushed, recording_name_conn)
    #signs.record(skeleton, letters = ['_'])
    signs.loadRecordings(letters = ['_', '-', '+', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I','K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y'])
    #signs.record(skeleton, letters = ['Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y'])
    
    signs.runAverageAngleComparison(skeleton, push_keys = True)
   
    
    while True:
        if True:
        #if skeleton.isReady(): 
            #skeleton.setFingerBoneGroups() # Done to create bone tree
            #print("\nFinger Hierarchies:")
            #skeleton.printFingerGroups() 

            time.sleep(2)
            left_end, right_end = determine_rotation_axis(skeleton)
            
            time.sleep(2)
            up_end, down_end = determine_rotation_axis(skeleton)

            time.sleep(2)
            closed_fist = StaticMovement(name = "closed", load = False)

            
            video_parent_conn.send(45.0)
            time.sleep(1)
            video_parent_conn.send(45.0)
            old_yaw = 0.0
            old_pitch = 0.0
            frames = 0

            movement1 = StaticMovement(name = "1", load = False)
            
            run = False
            was_closed = False
            while True:
                #print(sensitivity_slider.value)
                if shutdown.value == 1:
                    return
                if record_button_pushed.value == 1:
                    print("recieved")
                    movement1.record(skeleton = skeleton, num_seconds = 3, fps = 30, location = True, rotation = True, save = False)
                    print(" Done Recording.\n")
                    movement1.rotation_averages_quat = quaternionAverage(movement1.rotations_array_quat)
                    movement1.calculateAngleAverages()
                    
                    with lock:
                        record_button_pushed.value = 0
                    run = True

                if save_button_pushed.value == 1:
                    movement1.saveToCSV()

                    pose_name = None
                    while not pose_name:
                        pose_name = pose_name_conn.recv() # Receiving pose name from pipe

                    unique_identifier = None
                    while not unique_identifier:
                        unique_identifier = identifier_conn.recv() # Receiving pose name from pipe
                    
                    print(pose_name + "_" + unique_identifier)

                    with lock:
                        save_button_pushed.value = 0
                
                if load_button_pushed.value == 1:
                    movement1.loadFromCSV()
                    movement1.rotation_averages_quat = quaternionAverage(movement1.rotations_array_quat)
                    movement1.calculateAngleAverages()
                    with lock:
                        load_button_pushed.value = 0
                    run = True
                    

                if run:
                    is_closed = averageRotationComparison(movement1, skeleton)
                    if is_closed and was_closed:
                        new_yaw = axisDistance(left_end, right_end, skeleton)
                        new_pitch = axisDistance(up_end, down_end, skeleton)
                        if new_yaw != None:

                            #new_yaw = projection_onto_axis(left_end, right_end, skeleton) -0.5
                            #new_pitch = projection_onto_axis(up_end, down_end, skeleton) -0.5
                            video_parent_conn.send((old_yaw - new_yaw) * sensitivity_slider.value)
                            video_parent_conn_2.send((old_pitch - new_pitch) * sensitivity_slider.value)
                            old_yaw = new_yaw
                            old_pitch = new_pitch
                            time.sleep(.02)
                            was_closed = True
                        
                    elif is_closed and not was_closed:
                        new_yaw = projection_onto_axis(left_end, right_end, skeleton) -0.5
                        new_pitch = projection_onto_axis(up_end, down_end, skeleton) -0.5
                        old_yaw = new_yaw
                        old_pitch = new_pitch
                        video_parent_conn.send((old_yaw - new_yaw) * sensitivity_slider.value)
                        video_parent_conn_2.send((old_pitch - new_pitch) * sensitivity_slider.value)
                        time.sleep(.02)
                        was_closed = True
                    else: 
                        was_closed = False
                    

def dragAndDrop():
    pass
"""
            time.sleep(1)
            movement2 = StaticMovement(name = "2")
            movement2.record(skeleton = skeleton, num_seconds = 3, fps = 30, location = True, rotation = True)
            print(" Done Recording.\n")
            #movement1.calculateAverages() # Done to prepare nearestNeighbor. Should refactor
            movement2.rotation_averages_quat = quaternionAverage(movement2.rotations_array_quat)
            movement2.calculateAngleAverages()

            time.sleep(1)
            movement3 = StaticMovement(name = "3")
            movement3.record(skeleton = skeleton, num_seconds = 3, fps = 30, location = True, rotation = True)
            print(" Done Recording.\n")
            #movement1.calculateAverages() # Done to prepare nearestNeighbor. Should refactor
            movement3.rotation_averages_quat = quaternionAverage(movement3.rotations_array_quat)
            movement3.calculateAngleAverages()

            time.sleep(1)
            movement4 = StaticMovement(name = "4")
            movement4.record(skeleton = skeleton, num_seconds = 3, fps = 30, location = True, rotation = True)
            print(" Done Recording.\n")
            #movement1.calculateAverages() # Done to prepare nearestNeighbor. Should refactor
            movement4.rotation_averages_quat = quaternionAverage(movement4.rotations_array_quat)
            movement4.calculateAngleAverages()
            printed = None
            
            #time.sleep(2)
    
            #while True:
                # Loop to continously run Chosen Algorithm
                #angleAverageComparison(movement1, skeleton, movement1.hand_finger_angle_averages)
              
                letter = None
                p = None
                p = averageRotationComparison(movement1, skeleton)
                if p != None:
                    letter = p
                p = averageRotationComparison(movement2, skeleton)
                if p != None:
                    letter = p
                p = averageRotationComparison(movement3, skeleton)
                if p != None:
                    letter = p
                p = averageRotationComparison(movement4, skeleton)
                if p != None:
                    letter = p
                if letter != None:
                    if printed != letter:
                        print(letter)
                    printed = letter
            
                
                #print(skeleton.getBoneRotations()[9:12])
                #movement1.nearestNeighbor(skeleton)

    while True:
        # Second loop for testing. Currently not used
        if skeleton.isReady():
            pass
            #print(skeleton.getBoneRotations()[20:25])
"""
"""
while False:
                
                start_time = time.time()
                new_yaw = projection_onto_axis(left_end, right_end, skeleton) -0.5
                video_parent_conn.send((old_yaw - new_yaw) * sensitivity_slider.value)
                old_yaw = new_yaw
                current_time = time.time()
                frames += 1
                frame_rate = 1/(time.time()-start_time)
                time.sleep(.02)
"""
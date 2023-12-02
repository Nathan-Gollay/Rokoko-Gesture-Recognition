"""
Main computing driver. Separate Process from Sampling (blender_access) or main.

Author: Nathan Gollay
"""
# External Libraries
import time
import multiprocessing
import string
from threading import Thread
from collections import deque

# Internal Files
from classes.Skeleton import Skeleton
from classes.StaticMovement import StaticMovement
from Compute.rotations import *
from Compute.pose_detection_algorithms import *
from Compute.projection_onto_axis import *
from classes.SignLanguage import SignLanguage
from classes.MouseController import MouseController
from pynput.mouse import Button, Controller
from MouseAndKeyboard.mouse import *
from MouseAndKeyboard.mouse import *

def computePROCESS(skeleton, child_conn, record_button_pushed, save_button_pushed, load_button_pushed, 
        pose_name_conn, identifier_conn, video_parent_conn, video_parent_conn_2, skeleton_ready, 
        shutdown, sensitivity_slider, recording_name_conn, bone_name_conn):
    
    lock = multiprocessing.Lock()
    while skeleton_ready.value != 1:
        time.sleep(.1)
        
    while skeleton.bone_names == None:
        skeleton.bone_names = bone_name_conn.recv()

    skeleton.setFingerBoneGroups() # Done to create bone tree
    print("\nFinger Hierarchies:")
    skeleton.printFingerGroups() 

    mode = 3
    if mode == 1:
        mouseControl(skeleton, sensitivity_slider)
    if mode == 2: 
        mouseAndSignLanguage(skeleton, sensitivity_slider, record_button_pushed, recording_name_conn)
    
    left_end, right_end, up_end, bottom_end = videoDragDrop1D(skeleton, child_conn, record_button_pushed, save_button_pushed, load_button_pushed, 
        pose_name_conn, identifier_conn, video_parent_conn, video_parent_conn_2, skeleton_ready, 
        shutdown, sensitivity_slider, recording_name_conn, bone_name_conn)

    videoDragDrop2D(skeleton, child_conn, record_button_pushed, save_button_pushed, load_button_pushed, 
        pose_name_conn, identifier_conn, video_parent_conn, video_parent_conn_2, skeleton_ready, 
        shutdown, sensitivity_slider, recording_name_conn, bone_name_conn, left_end, right_end, up_end, 
        bottom_end)

    runSignLanguage(skeleton, record_button_pushed, recording_name_conn)


def runSignLanguage(skeleton, record_button_pushed, recording_name_conn):
    alphabet = string.ascii_uppercase
    signs = SignLanguage("Nathan", record_button_pushed, recording_name_conn)
    signs.loadRecordings(letters = ['_', '-', '+', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I','K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y'])

    signs.runAverageAngleComparison(skeleton, push_keys = True) 

def videoDragDrop2D(skeleton, child_conn, record_button_pushed, save_button_pushed, load_button_pushed, 
        pose_name_conn, identifier_conn, video_parent_conn, video_parent_conn_2, skeleton_ready, 
        shutdown, sensitivity_slider, recording_name_conn, bone_name_conn, left_end, right_end, up_end, down_end):
    lock = multiprocessing.Lock()
    while True:
        time.sleep(2)
        #left_end, right_end = determine_rotation_axis(skeleton)
            
        #time.sleep(2)
        #up_end, down_end = determine_rotation_axis(skeleton)

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

        xy_queue = deque(maxlen = 5)

        while True:
            if shutdown.value == 1:
                return

            if load_button_pushed.value == 1:
                load_button_pushed.value = 0
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
                    if new_yaw != None and old_yaw != None:
                        #new_yaw = projection_onto_axis(left_end, right_end, skeleton) -0.5
                        #new_pitch = projection_onto_axis(up_end, down_end, skeleton) -0.5
                        #print("send")
                        xy_queue.append((new_yaw, new_pitch))
                        new_yaw, new_pitch = simpleMovingAverage(list(xy_queue), 7)
                        video_parent_conn.send((old_yaw - new_yaw) * sensitivity_slider.value)
                        
                        old_yaw = new_yaw
                        was_closed = True

                    if new_pitch != None and old_pitch != None:
                        video_parent_conn_2.send((old_pitch - new_pitch) * sensitivity_slider.value)
                        old_pitch = new_pitch
                        was_closed = True
                        
                elif is_closed and not was_closed:
                    new_yaw = axisDistance(left_end, right_end, skeleton)
                    new_pitch = axisDistance(up_end, down_end, skeleton)
                    #new_yaw = projection_onto_axis(left_end, right_end, skeleton) -0.5
                    #new_pitch = projection_onto_axis(up_end, down_end, skeleton) -0.5
                    old_yaw = new_yaw
                    old_pitch = new_pitch
                    if new_yaw != None and old_yaw != None and new_pitch != None and old_pitch != None:
                        xy_queue.append((new_yaw, new_pitch))
                        new_yaw, new_pitch = simpleMovingAverage(list(xy_queue), 7)

                        video_parent_conn.send((old_yaw - new_yaw) * sensitivity_slider.value)
                        video_parent_conn_2.send((old_pitch - new_pitch) * sensitivity_slider.value)
                    time.sleep(.02)
                    was_closed = True
                else: 
                    was_closed = False
            time.sleep(.01)

def videoDragDrop1D(skeleton, child_conn, record_button_pushed, save_button_pushed, load_button_pushed, 
        pose_name_conn, identifier_conn, video_parent_conn, video_parent_conn_2, skeleton_ready, 
        shutdown, sensitivity_slider, recording_name_conn, bone_name_conn):
    lock = multiprocessing.Lock()
    while True:
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
            if shutdown.value == 1:
                return
            
            if load_button_pushed.value == 1:
                load_button_pushed.value = 0
                return left_end, right_end, up_end, down_end

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
            """
            if load_button_pushed.value == 1:
                movement1.loadFromCSV()
                movement1.rotation_averages_quat = quaternionAverage(movement1.rotations_array_quat)
                movement1.calculateAngleAverages()
                with lock:
                    load_button_pushed.value = 0
                run = True
            """
            if run:
                is_closed = averageRotationComparison(movement1, skeleton)
                if is_closed and was_closed:
                    new_yaw = axisDistance(left_end, right_end, skeleton)
                    
                    if new_yaw != None:
                        #new_yaw = projection_onto_axis(left_end, right_end, skeleton) -0.5
                        #new_pitch = projection_onto_axis(up_end, down_end, skeleton) -0.5
                        #print("send")
                        video_parent_conn.send((old_yaw - new_yaw) * sensitivity_slider.value)
                        
                        old_yaw = new_yaw
                        was_closed = True
                        
                elif is_closed and not was_closed:
                    new_yaw = axisDistance(left_end, right_end, skeleton)
                    #new_yaw = projection_onto_axis(left_end, right_end, skeleton) -0.5
                    #new_pitch = projection_onto_axis(up_end, down_end, skeleton) -0.5
                    old_yaw = new_yaw
                    
                    video_parent_conn.send((old_yaw - new_yaw) * sensitivity_slider.value)
                    time.sleep(.02)
                    was_closed = True
                else: 
                    was_closed = False

def mouseControl(skeleton, sensitivity_slider):
    # Function to control mouse pointer with glove
    mouse = MouseController(skeleton = skeleton)
    #mouse.setPointerPose()
    mouse.calibrateMouse()
    Mouse = Controller()
    old_y = 300.0
    old_x = 400.0
    
    movement1 = StaticMovement(name = "1", load = False)
    movement1.record(skeleton = skeleton, num_seconds = 3, fps = 30, location = True, rotation = True, save = False)
    print(" Done Recording.\n")
    movement1.rotation_averages_quat = quaternionAverage(movement1.rotations_array_quat)
    movement1.calculateAngleAverages()
    time.sleep(1)

    movement2 = StaticMovement(name = "1", load = False)
    movement2.record(skeleton = skeleton, num_seconds = 3, fps = 30, location = True, rotation = True, save = False)
    print(" Done Recording.\n")
    movement2.rotation_averages_quat = quaternionAverage(movement2.rotations_array_quat)
    movement2.calculateAngleAverages()
    
    is_pointer = False
    is_click = False
    was_click = False

    #parent, child = multiprocessing.Pipe()
    while True:
        
    
        is_pointer = averageRotationComparison(movement1, skeleton, return_total = False) 
        is_click = averageRotationComparison(movement2, skeleton, return_total = False) and not is_pointer
            
        """
        if is_pointer_val < 2.5:
            is_pointer = True
        
        elif is_click < 2.5:
            is_pointer = False
            is_click = True
        
        else:
            is_pointer = False
            is_click = False
        """
        if is_pointer and not was_click:
            x, y = mouse.getMousePositionAxis()
            if x != None and y != None and old_x != None and old_y != None:
                Mouse.move(-(old_x - x) * 100 * sensitivity_slider.value, -(old_y - y) * 100 * sensitivity_slider.value)
                #mouse.move((-(old_x - x), -(old_y - y)), sensitivity_slider.value)
            old_x = x
            old_y = y
            time.sleep(.05)
        
        if is_pointer and was_click:
            Mouse.release(Button.left)
            x, y = mouse.getMousePositionAxis()
            if x != None and y != None and old_x != None and old_y != None:
                Mouse.move(-(old_x - x) * 100 * sensitivity_slider.value, -(old_y - y) * 100 * sensitivity_slider.value)
                #mouse.move((-(old_x - x), -(old_y - y)), sensitivity_slider.value)
            old_x = x
            old_y = y
            time.sleep(.05)
        
        if is_click and not was_click:
            Mouse.press(Button.left)
            Mouse.release(Button.left)
            time.sleep(.1)
            Mouse.press(Button.left) 
            x, y = mouse.getMousePositionAxis()
            if x != None and y != None and old_x != None and old_y != None:
                Mouse.move(-(old_x - x) * 100 * sensitivity_slider.value, -(old_y - y) * 100 * sensitivity_slider.value)
                #mouse.move((-(old_x - x), -(old_y - y)), sensitivity_slider.value)
            old_x = x
            old_y = y
            was_click = True

        if is_click and was_click:
            x, y = mouse.getMousePositionAxis()
            if x != None and y != None and old_x != None and old_y != None:
                Mouse.move(-(old_x - x) * 100 * sensitivity_slider.value, -(old_y - y) * 100 * sensitivity_slider.value)
                #mouse.move((-(old_x - x), -(old_y - y)), sensitivity_slider.value)
            old_x = x
            old_y = y
            was_click = True
        
        if was_click and not is_click and not is_pointer:
            Mouse.release(Button.left)
            was_click = False
        
        if was_click and not is_click and not is_pointer:
            Mouse.release(Button.left)
            was_click = False

    
        
        


def mouseAndSignLanguage(skeleton, sensitivity_slider, record_button_pushed, recording_name_conn):    
    # Function to control mouse pointer with glove
    
    alphabet = string.ascii_uppercase
    signs = SignLanguage("Nathan", record_button_pushed, recording_name_conn)
    signs.loadRecordings(letters = ['_', '-', '+', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I','K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y'])
    sign_thread = Thread(target=signs.runAverageAngleComparison, args =(skeleton,))
    
    
    mouse = MouseController(skeleton = skeleton)
    #mouse.setPointerPose()
    mouse.calibrateMouse()
    Mouse = Controller()
    old_y = 300.0
    old_x = 400.0
    
    movement1 = StaticMovement(name = "1", load = False)
    movement1.record(skeleton = skeleton, num_seconds = 3, fps = 30, location = True, rotation = True, save = False)
    print(" Done Recording.\n")
    movement1.rotation_averages_quat = quaternionAverage(movement1.rotations_array_quat)
    movement1.calculateAngleAverages()
    time.sleep(1)

    movement2 = StaticMovement(name = "1", load = False)
    movement2.record(skeleton = skeleton, num_seconds = 3, fps = 30, location = True, rotation = True, save = False)
    print(" Done Recording.\n")
    movement2.rotation_averages_quat = quaternionAverage(movement2.rotations_array_quat)
    movement2.calculateAngleAverages()
    
    sign_thread.start()

    while True:
        #print("\nNormalized: ", mouse.getMousePositionAxis())
        is_pointer = averageRotationComparison(movement1, skeleton)
        is_click = averageRotationComparison(movement2, skeleton)
        if is_pointer:
            x, y = mouse.getMousePositionAxis()
            #print(old_x - x, old_y - y)
            Mouse.move(-(old_x - x) * 100 * sensitivity_slider.value, -(old_y - y) * 100 * sensitivity_slider.value)
            old_x = x
            old_y = y
            time.sleep(.05)
        if is_click:
            Mouse.click(Button.left, 1) 
            time.sleep(2) 
  
    

    
   
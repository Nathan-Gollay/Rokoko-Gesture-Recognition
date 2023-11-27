"""
Driver for whole program. Process hnadling, data initialization
Author: Nathan Gollay
"""
#External Libraries
import threading
import multiprocessing as mp
from multiprocessing import Process, Pipe, Array, Lock, Manager, Value
from multiprocessing.managers import BaseManager
import subprocess
import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QSlider, QLabel
from PyQt6.QtCore import Qt

#Internal Files
from classes.Skeleton import Skeleton
from Blender.blender_access import *
from Compute.compute_driver import computePROCESS
from gui.main_window import SliderDemo
from api.api_sampler import *
from vlc_player.bindings.python.test import start


LOCAL_IP = '127.0.0.1'
PORT = 65432

def main():
    #mp.set_start_method('fork') # Needs to be done for compatibility to newer python verions 
    mp.set_start_method('spawn')
    
    record_button_pushed = Value('i', 0)
    save_button_pushed = Value('i', 0)
    load_button_pushed = Value('i', 0)
    skeleton_ready = Value('i', 0)
    shutdown = Value('i', 0)
    sensitivity_slider = Value('i', 0)
    
    pose_name_parent_conn, pose_name_child_conn = Pipe()
    identifier_name_parent_conn, identifier_name_child_conn = Pipe()
    video_parent_conn, video_child_conn = Pipe()
    video_parent_conn_2, video_child_conn_2 = Pipe()
    recording_name_parent_conn, recording_name_child_conn = Pipe()
    bone_name_parent_conn, bone_name_child_conn = Pipe()

    bone_name_parent_conn, bone_name_child_conn = Pipe()
    skeleton = Skeleton(None, pipe = bone_name_parent_conn)
    #SAMPLE_PROCESS = Process(target=blenderSamplePROCESS, args=(PORT,LOCAL_IP, child_conn, skeleton))
    SAMPLE_PROCESS = Process(target=sampler, args=(skeleton, skeleton_ready, shutdown, 
        bone_name_parent_conn))
    SAMPLE_PROCESS.start()

    COMSUMER_PROCESS = Process(target=computePROCESS, args =(skeleton, bone_name_child_conn, 
        record_button_pushed, save_button_pushed, load_button_pushed, pose_name_child_conn, 
        identifier_name_child_conn, video_parent_conn, video_parent_conn_2, skeleton_ready, 
        shutdown, sensitivity_slider, recording_name_child_conn, bone_name_child_conn))
    COMSUMER_PROCESS.start()
    
    
    child_process = Process(target=start, args=(video_child_conn, video_child_conn_2, "hike.mp4", shutdown))
    child_process.start()
    #time.sleep(3)
    video_parent_conn.send("1")
    
    """
    VIDEO_SUBPROCESS = "vlc/bindings/python/test.py"
    args = [str(video_child_conn.fileno()), 'hike.mp4']
    subprocess.run(['python', VIDEO_SUBPROCESS] + args, pass_fds=[video_child_conn.fileno()])
    """
    #Uncomment to enable GUI
    
    app = QApplication(sys.argv)
    window = SliderDemo(record_button_pushed, save_button_pushed, load_button_pushed, pose_name_parent_conn,
        identifier_name_parent_conn, sensitivity_slider, recording_name_parent_conn)
    sys.exit(app.exec())
    app.exec()

    shutdown.value = 1

    SAMPLE_PROCESS.join()
    COMSUMER_PROCESS.join()
    child_process.join()

    sys.exit()

if __name__ == "__main__":
    #BaseManager.register('Skeleton', Skeleton)
    main()


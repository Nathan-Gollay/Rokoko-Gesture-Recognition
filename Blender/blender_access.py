"""
Handles all Communication With Blender

Author: Nathan Gollay
"""


import socket
import time
import json
import signal

HOST = '127.0.0.1' # localhost
PORT = 65432 # Port set to same in blender
conn = None 
s = None

def start_server(PORT, HOST, child_conn, skeleton):
    # Function to continously sample socket
    global conn
    global s
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print("Server started and listening for connections...")
        
        # Wait for a connection
        conn, addr = s.accept()
        with conn:
            print('Connected by', addr)
            
            # Continuous loop to keep receiving data
            old_d = None
            while True:
                data_length = int.from_bytes(conn.recv(4), 'big') #Set Data Length
                data_str = conn.recv(data_length).decode() # Decode
                d = json.loads(data_str) # Handle JSON
                skeleton.update(d) 
                old_d = d # Not currently used


                """ Old Logic, if things go wrong maybe look here:"""
                #data = conn.recv(8192)  # You can adjust the buffer size as needed
                #if not data:
                    # If no data is received, the client might have disconnected
                  #  print("Client disconnected.")
                  #  break
                #print(d)d
                #if old_d:
                   # print(active_bones(d, old_d))
                #if not old_d:
                   # skeleton.setDimensions(d)  
                #child_conn.send(d)
                #print('Received:',d )
                #print(zlib.decompress(data).decode())
            conn.close()

def active_bones(frame1, frame2, position_threshold=0.01, rotation_threshold=0.1):
    # Determines the Active Bones by the changes between two frames
    active = []

    for bone1, bone2 in zip(frame1, frame2):
        bone_name_1, position_1, rotation_1 = bone1
        bone_name_2, position_2, rotation_2 = bone2

        # Ensure the bone names match between frames
        assert bone_name_1 == bone_name_2

        position_difference = [abs(a - b) for a, b in zip(position_1, position_2)]
        rotation_difference = [abs(a - b) for a, b in zip(rotation_1, rotation_2)]

        if any(diff > position_threshold for diff in position_difference) or \
                any(diff > rotation_threshold for diff in rotation_difference):
            active.append(bone_name_1)

    return active

def signal_handler(signum, frame):
    # Add signal handling mumbo jumbo in here
    global conn
    if conn:
        print("Shutting down server...")
        conn.close()
    if s:
        s.close()

def blenderSamplePROCESS(PORT, HOST, child_conn, skeleton):
    # Handles sampling process from blender
    signal.signal(signal.SIGINT, signal_handler) # Signal Handling
    signal.signal(signal.SIGTERM, signal_handler) # Signal Handling

    start_server(PORT, HOST, child_conn, skeleton) # Start Listening 


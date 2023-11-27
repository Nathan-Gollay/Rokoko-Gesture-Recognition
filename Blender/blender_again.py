"""
Handles interaction with blender

Author: Nathan Gollay
CURRENTLY OBSOLETE
"""

import socket
import time
import signal

HOST = '127.0.0.1'
PORT = 65432
conn = None
s = None

""" Currently Obsolete INSTEAD: see blender-access """

def start_server():
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



def signal_handler(signum, frame):
    global conn
    if conn:
        print("Shutting down server...")
        conn.close()
    # If you need to close the server socket as well
    if s:
        s.close()
    exit(0)

# Set up signal handling
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)



def receive_data_from_conn(conn):
    # Receive the 4-byte length header
    length_header = conn.recv(4)
    if not length_header:
        return None
    data_length = struct.unpack('!I', length_header)[0]  # Unpack the length
    
    # Receive the compressed data based on the unpacked length
    chunks = []
    bytes_received = 0
    while bytes_received < data_length:
        chunk = conn.recv(min(data_length - bytes_received, 1024))
        if not chunk:
            return None  
        chunks.append(chunk)
        bytes_received += len(chunk)

    compressed_data = b''.join(chunks)
    return zlib.decompress(compressed_data).decode()

start_server()

while True:
    try:
        data = receive_data_from_conn(conn)
        if data:
            print('Received:')
            print(data)
        else:
            print("Client disconnected.")
            break
    except Exception as e:
        print(f"Error: {e}")
conn.close()

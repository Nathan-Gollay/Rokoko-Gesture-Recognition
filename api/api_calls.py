"""
Library of API Calls

Authors: Nathan Gollay, Rokoko
"""

import requests

IP_ADDRESS = '127.0.0.1'
PORT = '14053'
#IP_ADDRESS = '192.168.1.2' # Replace with actual ip address
#PORT = '14053' # Replace with actual port
API_KEY = '1234' # Replace with actual api key
COMMAND_POSE = 'pose'
COMMAND_INFO = 'info'
COMMAND_LIVESTREAM = 'livestream'

def getPose():
    # Function for accessing pose information of Rokoko's api
    response = None
    try:
        response = requests.post(f"http://{IP_ADDRESS}:{PORT}/v2/{API_KEY}/{COMMAND_POSE}",
        json = {
            'name' : 'Nathan', # empty for a first found actor or character in the scene
            'mode' : 'motion', # could be definition, motion or reference
            'space' : 'local' # could be local, global or localref
            }
        )
    except Exception as e:
        print (e)
    finally:
    	if response is not None:
        	return(response.json())

#getPose()

def getPoseDefinition():
    
    response = None
    try:
        response = requests.post(f"http://{IP_ADDRESS}:{PORT}/v2/{API_KEY}/{COMMAND_POSE}",
        json = {
            'name' : '', # empty for a first found actor or character in the scene
            'mode' : 'definition', # could be definition, motion or reference
            'space' : 'local' # could be local, global or localref
        }
        )
    except Exception as e:
    	print (e)
    finally:
    	if response is not None:
        	return(response.json())


def getInfo():
    response = None
    try:
        response = requests.post(f"http://{IP_ADDRESS}:{PORT}/v2/{API_KEY}/{COMMAND_INFO}",
        json = {
            'devices_info': False, # return a list of all live devices in the scene
            'clips_info': False, # return a list of all recorded clips in the scene
            'actors_info' : True, # return a list of all actors
            'characters_info' : True # return a list of all character
        }
        )
    except Exception as e:
        print (e)
    finally:
        if response is not None:
            return(response.json())

def startLivestream():
    response = None
    try:
        response = requests.post(f"http://{IP_ADDRESS}:{PORT}/v2/{API_KEY}/{COMMAND_LIVESTREAM}",
        json = {
            'enabled' : True
        }
        ) 
    except Exception as e:
        print (e)
    if response is not None:
        print(response.json())


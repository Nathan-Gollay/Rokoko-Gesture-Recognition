"""
Basic sample function logic

Author: Nathan Gollay
"""

from api.api_calls import *
import time
import multiprocessing as mp

def sampler(skeleton, skeleton_ready, shutdown, bone_name_pipe, sample_rate = .01):
    #Function to sample an api call on a given interval
    
    active = []
    rokoko_tries = 0
    while len(active) != 22:
        rokoko_tries +=1
        for i in range(500):
            throw_away = getPose()
    
        arr = []
        for i in range(500):
            arr.append(getPose()['parameters'])
        active = getActiveBones(arr)
        if rokoko_tries >= 5:
            shutdown.value = 1
            raise Exception("Restart Rokoko and tell their developers to get their shit together.")
    
    bone_names = getPoseDefinition()['parameters']
    active_bone_names = []


    print("\nActive Bones:\n")
    for i in active:
        active_bone_names.append(bone_names[i-1])
        print(bone_names[i-1])
    
    bone_name_pipe.send(active_bone_names)
    
    lock = mp.Lock()
    with lock:
        skeleton_ready.value = 1
        
    while not shutdown.value:
        skeleton.updateWithRokoko(convertToArray(active, getPose()['parameters']))

def isActive(entry1, entry2):
    # A helper function to check if two entries are different.
    return any(entry1.get(key) != entry2.get(key) for key in entry1 if key != 'IsIdentity')

def getActiveBones(list_of_instances):
    # Find bones that are active over 50 instances.

    active_entries = []
    for i in range(len(list_of_instances) - 1):
        current_instance = list_of_instances[i]
        next_instance = list_of_instances[i + 1]
        for j, entry in enumerate(current_instance):
            if isActive(entry, next_instance[j]):
                active_entries.append(j)
    # Remove duplicates by converting to a set and back to a list.
    return list(set(active_entries))

def convertToArray(active_indexes, pose):
    # Decodes data into quaternion arrays
    keys = ['X', 'Y', 'Z', 'W']
    array = []
    for i in active_indexes:
        for key in keys:
            array.append(pose[i][key])
    assert len(array) == len(active_indexes) * 4
    return(array)

    
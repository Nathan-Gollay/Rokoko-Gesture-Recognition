"""
Basic sample function logic
Author: Nathan Gollay
"""

from api.api_calls import *
import time
import multiprocessing as mp

def sampler(skeleton, skeleton_ready, shutdown, bone_name_pipe, sample_rate = .01):
    #Function to sample an api call on a given interval
    for i in range(500):
        throw_away = getPose()
    
    arr = []
    for i in range(500):
        arr.append(getPose()['parameters'])
    active = find_active_entries(arr)
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
    #getActiveBones()
    #print(getPoseDefinition())
    
def isActive(old_rotation, new_rotation):
    for old, new in zip(old_rotation, new_rotation):
       # print(old, new)
        if old != new:
            return True
    return False 

def getActiveBones():
    old_data = None
    for i in range(500):
        time.sleep(.1)
        data = getPose()
        if data['parameters'] == None:
            raise Exception("Rokoko be fucking up again")
        bone_rotations_json = data['parameters']
        active_indexes = []
        #print(active_indexes)
        #print(bone_rotations_json)
        if old_data != None:
            print(old_data[50])
            for old, new in zip(old_data, bone_rotations_json):
                if isActive(old, new):
                   pass
                   # print(i)
        old_data = bone_rotations_json

def is_active(entry1, entry2):
    # A helper function to check if two entries are different.
    return any(entry1.get(key) != entry2.get(key) for key in entry1 if key != 'IsIdentity')

def find_active_entries(list_of_instances):
    # Find entries that are active over 50 instances.
    active_entries = []
    for i in range(len(list_of_instances) - 1):
        current_instance = list_of_instances[i]
        next_instance = list_of_instances[i + 1]
        for j, entry in enumerate(current_instance):
            if is_active(entry, next_instance[j]):
                active_entries.append(j)
    # Remove duplicates by converting to a set and back to a list.
    return list(set(active_entries))

def convertToArray(active_indexes, pose):
    keys = ['X', 'Y', 'Z', 'W']
    array = []
    for i in active_indexes:
        for key in keys:
            array.append(pose[i][key])
    #print(array)
    assert len(array) == len(active_indexes) * 4
    return(array)
#sampler()
    
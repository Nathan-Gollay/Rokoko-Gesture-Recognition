"""
Node of finger bone tree structure

Author: Nathan Gollay
"""
class FingerNode:
    # Tree List structure to store bone hierarchies
    def __init__(self, name, bone_type, finger_num):
        self.root = None
        self.next_bones = None # stored as array of nodes if root, one node object if finger
        self.prev_bone = None
        
        self.name = name
        self.index = None
        self.type = bone_type # Metacarpal: 1, Proximal: 2, Medial: 3, Distal: 4
        self.finger_num = finger_num # Thumb, Pointer, etc

    def insert(self, node):
        # Do not use with root! instead: root.next_bones = [new_finger_node]
        if self.root == self:
            raise Exception("Can't use this function on root node")
        if self.next_bones:
            node.next_bones = self.next_bones
            self.next_bones.prev_bone = node
        self.next_bones = node
        node.prev_bone = self
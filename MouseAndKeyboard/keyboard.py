from pynput.keyboard import Controller, Key
import time

def pushKey(char):
    keyboard = Controller()
    key = char
    if char == '-':
        key = Key.backspace
    if char == '_':
        key = Key.space
    if char == '+':
        key = Key.enter
    try:
        keyboard.press(key)
        keyboard.release(key)
    except:
        raise Exception("Keyboard control issue")

#FIRST SENTENCE WRITTEN WITH GLOVES
#I CAN TYPE WITH MY FINGERS PRETTY ACURATELY THIS IS REALLY COOL IM REALLY EXCITED FOR THIS TO BE WORKING IM PROUD OF MYSELF
from pynput.mouse import Button, Controller
import time

mouse = Controller()

while True:
    print(mouse.position)
    time.sleep(1)

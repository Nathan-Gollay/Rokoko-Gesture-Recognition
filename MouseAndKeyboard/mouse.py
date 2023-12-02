from pynput.mouse import Button, Controller
import time

mouse = Controller()

def printMousePositions():
    while True:
        print(mouse.position)
        mouse.move(100, -100)
        time.sleep(1)

def simpleMovingAverage(deltas, window_size):
    if len(deltas) < window_size:
        return sum(dx for dx, _ in deltas) / len(deltas), sum(dy for _, dy in deltas) / len(deltas)

    recent_deltas = deltas[-window_size:]
    avg_dx = sum(dx for dx, _ in recent_deltas) / window_size
    avg_dy = sum(dy for _, dy in recent_deltas) / window_size

    return avg_dx, avg_dy

deltas = ((1, 1), (2, 2), (3, 3), (4, 4), (100, 100), (100, 100), )
window_size = 5

print(simpleMovingAverage(deltas, window_size))
from pynput.mouse import Button, Controller
import time
from collections import deque

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

def getMomentumArray(delta_positions, window_size = 7, initial_momentum_factor = 0.5, decay_rate = 0.9):
    """
    Apply a momentum effect with decay to a list of delta positions.

    :param delta_positions: List of tuples containing (delta_x, delta_y)
    :param window_size: Number of recent points to consider for averaging
    :param initial_momentum_factor: Initial momentum factor
    :param decay_rate: Rate at which momentum decays each step
    :return: List of tuples containing (new_delta_x, new_delta_y) with momentum and decay applied
    """
    if window_size <= 0:
        raise ValueError("Window size must be a positive integer")

    # Initialize lists to store the averaged velocities
    momentum_deltas = []

    # Initialize momentum factor
    momentum_factor = initial_momentum_factor

    # Iterate over the delta_positions list
    for i in range(len(delta_positions)):
        # Calculate the window start and end
        window_start = max(0, i - window_size + 1)
        window_end = i + 1

        # Calculate average delta_x and delta_y in the current window
        avg_delta_x = sum(delta[0] for delta in delta_positions[window_start:window_end]) / (window_end - window_start)
        avg_delta_y = sum(delta[1] for delta in delta_positions[window_start:window_end]) / (window_end - window_start)

        # Apply the momentum factor
        new_delta_x = avg_delta_x * momentum_factor
        new_delta_y = avg_delta_y * momentum_factor

        # Append the result to the momentum_deltas list
        momentum_deltas.append((new_delta_x, new_delta_y))

        # Apply decay to the momentum factor
        momentum_factor *= decay_rate

    return momentum_deltas

# Example usage
delta_positions = [(1, 2), (2, 1), (3, 3), (4, 2)]  # Example list of delta positions
window_size = 3  # Window size for averaging
initial_momentum_factor = 0.5  # Initial momentum factor
decay_rate = 0.9  # Decay rate for momentum

momentum_effect = getMomentumArray(delta_positions, window_size, initial_momentum_factor, decay_rate)
print(momentum_effect)


#deltas = ((1, 1), (2, 2), (3, 3), (4, 4), (100, 100), (100, 100), )
#window_size = 5

#print(simpleMovingAverage(deltas, window_size))

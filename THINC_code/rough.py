import math

def calculate_distance(point1, point2):

    x1, y1 = point1
    x2, y2 = point2
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def calculate_slope(point1, point2):

    x1, y1 = point1
    x2, y2 = point2
    return (y2 - y1)/(x2 - x1)

def calculate_velocity(point1, point2, time_diff):

    return calculate_distance(point1, point2)/time_diff

# Example usage
pointA = (361, 220)
pointB = (257, 233)
delta_t = 0.6548388004302979

distance = calculate_distance(pointA, pointB)
slope = calculate_slope(pointA, pointB)
velocity = calculate_velocity(pointA, pointB, delta_t)

print()
print("="*20)
print(f"Distance between point A and point B: {distance}")
print(f"Slope between point A and point B: {slope}")
print(f"Velocity from point A to point B: {velocity}")
print("="*20)
print()


import pkg_resources

version = pkg_resources.get_distribution("antlr4-python3-runtime").version
print("antlr4-python3-runtime version:", version)


import omegaconf

print("omegaconf version:", omegaconf.__version__)

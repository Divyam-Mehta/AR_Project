import numpy as np
from vars import *


def pixelToWorld(m, n):
    # Function created with help from https://dsp.stackexchange.com/a/46591

    # Manually calibrated points (in pixels, with 0,0 at top left of conveyor area that camera sees)
    M = np.array([[96 ** 2, 96 * 64, 64 ** 2, 96, 64, 1],
                  [249 ** 2, 249 * 63, 63 ** 2, 249, 63, 1],
                  [435 ** 2, 435 * 52, 52 ** 2, 435, 52, 1],
                  [611 ** 2, 611 * 47, 47 ** 2, 611, 47, 1],
                  [101 ** 2, 101 * 295, 295 ** 2, 101, 295, 1],
                  [275 ** 2, 275 * 290, 290 ** 2, 275, 290, 1],
                  [426 ** 2, 426 * 304, 304 ** 2, 426, 304, 1],
                  [584 ** 2, 584 * 301, 301 ** 2, 584, 301, 1]])

    # Manually calibrated points (in inches, with 0,0 at bottom left of conveyor)
    # May need to convert this to the 0,0 at top left corner of conveyor
    R = np.array([[4, 17],
                  [12, 17],
                  [21.8, 17.9],
                  [30.75, 18],
                  [4, 3.6],
                  [13, 4],
                  [21, 3.4],
                  [29, 3.6]])
    
    # Form equation M * U = R. Solve for U to get coefficients in later equation
    U = np.dot(np.linalg.inv((np.dot(np.transpose(M), M))), np.dot(np.transpose(M), R))

    realX = U[0,0] * m ** 2 + U[1,0] * m * n + U[2,0] * n ** 2 + U[3,0] * m +  U[4,0] * n + U[5,0]
    realY = U[0,1] * m ** 2 + U[1,1] * m * n + U[2,1] * n ** 2 + U[3,1] * m +  U[4,1] * n + U[5,1]

    # Offset from marked point on the supporting rod where the camera was first calibrated at
    x_offset = 13

    # Maybe this?
    #print(np.linalg.inv(U))
    return realX + x_offset, realY


print(pixelToWorld(500, 500))



def pixelToMM(u, v):
    offset = 0
    
    # Place onions at four extreme cornors of the camera frame and map real world coordinates to camera frame in "features_mm_to_pixels_dict"
    features_mm_to_pixels_dict = {(0 + offset, 0): (1237, 316),
                                (0 + offset, 500): (1239, 34),
                                (1730 + offset, 0): (34, 336),
                                (1730 + offset, 500): (28, 58)}

    A = np.zeros((2 * len(features_mm_to_pixels_dict), 6), dtype=float)
    b = np.zeros((2 * len(features_mm_to_pixels_dict), 1), dtype=float)
    index = 0
    for XY, xy in features_mm_to_pixels_dict.items():
        X = XY[0]
        Y = XY[1]
        x = xy[0]
        y = xy[1]
        A[2 * index, 0] = x
        A[2 * index, 1] = y
        A[2 * index, 2] = 1
        A[2 * index + 1, 3] = x
        A[2 * index + 1, 4] = y
        A[2 * index + 1, 5] = 1
        b[2 * index, 0] = X
        b[2 * index + 1, 0] = Y
        index += 1
    # A @ x = b
    x, residuals, rank, singular_values = np.linalg.lstsq(A, b, rcond=None)

    pixels_to_mm_transformation_mtx = np.array([[x[0, 0], x[1, 0], x[2, 0]], [x[3, 0], x[4, 0], x[5, 0]], [0, 0, 1]])

    test_xy_1 = (u, v, 1)
    test_XY_1 = pixels_to_mm_transformation_mtx @ test_xy_1

    return test_XY_1

def mmToPixel(u, v):
    offset = 0
    
    # Place onions at four extreme cornors of the camera frame and map real world coordinates to camera frame in "mm_to_pixels"
    mm_to_pixels = {(0 + offset, 0): (1237, 316),
                                (0 + offset, 500): (1239, 34),
                                (1730 + offset, 0): (34, 336),
                                (1730 + offset, 500): (28, 58)}

    A = np.zeros((2 * len(mm_to_pixels), 6), dtype=float)
    B = np.zeros((2 * len(mm_to_pixels), 1), dtype=float)
    index = 0

    for world_coords, pixel_coords in mm_to_pixels.items():
        world_x = world_coords[0]
        world_y = world_coords[1]
        pixel_x = pixel_coords[0]
        pixel_y = pixel_coords[1]

        A[2 * index, 0] = pixel_x
        A[2 * index, 1] = pixel_y
        A[2 * index, 2] = 1
        A[2 * index + 1, 3] = pixel_x
        A[2 * index + 1, 4] = pixel_y
        A[2 * index + 1, 5] = 1
        B[2 * index, 0] = world_x
        B[2 * index + 1, 0] = world_y
        index += 1

    x, residuals, rank, singular_vars = np.linalg.lstsq(A, B, rcond=None)

    pixels_to_mm_transformation_mtx = np.array([[x[0, 0], x[1, 0], x[2, 0]], [x[3, 0], x[4, 0], x[5, 0]], [0, 0, 1]])
    mm_to_pixels = np.linalg.inv(pixels_to_mm_transformation_mtx)

    world = (u, v, 1)

    pixels = mm_to_pixels @ world

    return pixels

def mmToPixelProjector(u, v):
    x_offset = -75 #75
    y_offset = -100

    # Place onions at four extreme cornors of the camera frame and map real world coordinates to pygame dimensions in "features_mm_to_pixels_dict"
    features_mm_to_pixels_dict =  {(250 + x_offset, 0 + y_offset): (0, 0),
                                (325 + x_offset, 650 + y_offset): (0, 1080),
                                (1550 + x_offset, 0 + y_offset): (1920, 0),
                                (1480 + x_offset, 650 + y_offset): (1920, 1080)}


    
    A = np.zeros((2 * len(features_mm_to_pixels_dict), 6), dtype=float)
    b = np.zeros((2 * len(features_mm_to_pixels_dict), 1), dtype=float)
    index = 0
    for XY, xy in features_mm_to_pixels_dict.items():
        X = XY[0]
        Y = XY[1]
        x = xy[0]
        y = xy[1]
        A[2 * index, 0] = x
        A[2 * index, 1] = y
        A[2 * index, 2] = 1
        A[2 * index + 1, 3] = x
        A[2 * index + 1, 4] = y
        A[2 * index + 1, 5] = 1
        b[2 * index, 0] = X
        b[2 * index + 1, 0] = Y
        index += 1
    # A @ x = b
    x, residuals, rank, singular_values = np.linalg.lstsq(A, b, rcond=None)

    pixels_to_mm_transformation_mtx = np.array([[x[0, 0], x[1, 0], x[2, 0]], [x[3, 0], x[4, 0], x[5, 0]], [0, 0, 1]])


    mm_to_pixels_transformation_mtx = np.linalg.inv(pixels_to_mm_transformation_mtx)
    test_XY_2 = (u, v, 1)
    test_xy_2 = mm_to_pixels_transformation_mtx @ test_XY_2

    return test_xy_2
from cv2 import ROTATE_90_COUNTERCLOCKWISE
import numpy as np
from vars import *
from CentroidTracker import CentroidTracker
import cv2
import shutil
import math


# Checks when an onion made it past the anterior line
# Also takes an image of the onion
def anterior_check(objects, time, high_res_frame):
    for (objectId, centroid) in objects.items():
        if centroid[0] > ANT_LINE_X - X_LEEWAY and centroid[0] < ANT_LINE_X + X_LEEWAY:
            # Stores time that onion was at anterior line
            if objectId not in ant_times:
                ant_times[objectId] = time
                # Takes image of onion
                for i in range(len(centers)):
                    # If the center of the blob detector is the same from centroid tracking, store image in tempDB
                    if ((centroid[0] - CENTER_LEEWAY <= int(centers[i][0]) and centroid[0] + CENTER_LEEWAY >= int(centers[i][0])) and
                    (centroid[1] - CENTER_LEEWAY <= int(centers[i][1]) and centroid[1] + CENTER_LEEWAY >= int(centers[i][1]))):
                        if not os.path.isfile(TEMP_DB + "/tempImg_" + str(objectId) + ".bmp"):
                            print("Image Taken")
                            cv2.imwrite(TEMP_DB + "/tempImg_" + str(objectId) + ".bmp",
                            high_res_frame[boxes[i][1]:boxes[i][3], boxes[i][0]:boxes[i][2]])
                            # startY:endY, startX:endX for image cropping
                            # Also, write a way to scale BBox images for a higher resolution image



# Checks if an onion made it past posterior line or not
def posterior_check(objects):

    for (objectId, centroid) in objects.items():
        if centroid[0] > POST_LINE_X - X_LEEWAY and centroid[0] < POST_LINE_X + X_LEEWAY:
            if objectId not in post_ids:
                post_ids.append(objectId) 

# Defines whether onions are good or bad
def good_or_bad(time):
    
    for id in all_ids:
        # If onion passed the posterior camera, it is good
        if id in post_ids and id not in good_ids:
            good_ids.append(id)
            # Maybe add cleanup here to save ram, if time permits
        # If after a reasonable amount of time, the onion hasn't passed the
        # posterior camera, it is bad
        if id not in post_ids and id in ant_times and id not in bad_ids:
            print()
            print("Id -", id, "   |   Time:  ", time, "   |    Ant Times:  ", ant_times[id], "\n")
            print("="*100)
            if time - ant_times[id] > CAM_DIST:
                bad_ids.append(id)
            
# Makes each file have a unique file name
def unique_name(filepath):
    file, ext = os.path.splitext(filepath)
    i = 1

    while os.path.exists(filepath):
        filepath = file + "_" + str(i) + "_" + ext
        i = i + 1
    
    return filepath

# Sorts onions in tempDB to permDB based on IDs
# Call this after good_or_bad
def sort():
    for file in os.listdir(TEMP_DB):
        id = file[8:]
        id = id.replace(".bmp", "")

        if int(id) in good_ids:
            name = "good_onion"
            path = unique_name(GOOD_ONION_DB + "\\" + name + ".bmp")
            shutil.move(TEMP_DB + "\\" + file, path)

        if int(id) in bad_ids:
            name = "bad_onion"
            path = unique_name(BAD_ONION_DB + "\\" + name + ".bmp")
            shutil.move(TEMP_DB + "\\" + file, path)

def calibrate(ant_cap, post_cap, params):

    ct = CentroidTracker()

    tempBoxes = []
    tempCenters = []
    tempRects = []
    time1 = 0
    time2 = 0
    antNotFound = True
    postNotFound = True


    index = 0
    while True:
        ant_ret, ant_frame = ant_cap.read()
        post_ret, post_frame = post_cap.read()

        # High res frame for image capture
        high_res_frame = ant_frame.copy()

        ant_frame_process = ant_frame.copy()
        post_frame_process = post_frame.copy()

        # Rotate image
        ant_frame_process = cv2.rotate(ant_frame_process, ROTATE_90_COUNTERCLOCKWISE)

        # Lower res frames for tracking and cropped to only view the conveyor
        ant_frame_process = ant_frame_process[250:450, 150:480]
        post_frame_process = post_frame_process[165:435, 50:500]
        
        # Normalization of resolution across cameras (not needed when both cameras are same)
        ant_frame_process = cv2.resize(ant_frame_process, RESIZE_RES)
        post_frame_process = cv2.resize(post_frame_process, RESIZE_RES)

        # Combination of frames into one video
        process_frame = np.concatenate((ant_frame_process, post_frame_process), axis=1)
        
        # Process frame without any further modifications
        pure_process_frame = process_frame.copy()

        # Inverts process_frame for easier onion detection
        process_frame_invert = cv2.bitwise_not(process_frame)

        detector = cv2.SimpleBlobDetector_create(params)
        keypoints = detector.detect(process_frame_invert)
        
        for keypoint in keypoints:
            
            x = keypoint.pt[0]
            y = keypoint.pt[1]
            s = keypoint.size

            # Computes bounding box points via geometry
            area = (s/2) ** 2 * math.pi
            rectangle_formula = math.sqrt(area) / 1.5
        
            x1 = int(x - rectangle_formula)
            y1 = int(y - rectangle_formula)
            x2 = int(x + rectangle_formula)
            y2 = int(y + rectangle_formula)
            
            # Appends BBox coords to the list of tracked onions
            box = (x1, y1, x2, y2)
            tempRects.append(box)

            # Appends centroids to centers
            tempCenters.append((x, y))
            tempBoxes.append(box)
            
            # Displays BBox on frame
            cv2.rectangle(process_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        objects = ct.update(tempRects)

        if antNotFound:
            for (objectId, centroid) in objects.items():
                if centroid[0] > ANT_LINE_X - X_LEEWAY and centroid[0] < ANT_LINE_X + X_LEEWAY:        
                    time1 = index
                    print("T1:", time1)
                    antNotFound = False

        if not antNotFound and postNotFound:
            for (objectId, centroid) in objects.items():
                if centroid[0] > POST_LINE_X - X_LEEWAY and centroid[0] < POST_LINE_X + X_LEEWAY:
                    time2 = index
                    print("T2:", time2)
                    postNotFound = False
            
        if not antNotFound and not postNotFound:

            if time1 == time2:
                print("CALIBRATION FAILED")
                return -1
            else:
                return time2 - time1

            
        display_img = process_frame.copy()

        cv2.line(display_img, ANT_LINE_START, ANT_LINE_END, (0, 255, 0), 1)
        cv2.line(display_img, POST_LINE_START, POST_LINE_END, (0, 255, 0), 1)

        cv2.imshow("Onion Tracking Program", display_img)

        key = cv2.waitKey(1)
        if key == ord('q'):
            break

        index = index + 1

# Scales the camera pixelated onion to projected pixelated red/green onion
def scale(radius):

    realSize = radius * camNormalizedPixels

    projSize = realSize / projNormalizedPixels

    return projSize

# Scales BBox from tracking up to 4k resolution and takes image from 
# high res frame and stores it with an ID tagged to the image
# def scale_to_high_res():

def create_peak_mask(coordinates, image_shape):
    """
    Create a boolean array where True indicates the presence of peaks
    based on the provided coordinates.

    Parameters:
    - coordinates: Array of peak coordinates (e.g., output from peak_local_max)
    - image_shape: Shape of the input image

    Returns:
    - peak_mask: Boolean array with True indicating the presence of peaks
    """
    peak_mask = np.zeros(image_shape, dtype=bool)
    peak_mask[coordinates[:, 0], coordinates[:, 1]] = True
    return peak_mask

# Area of Rectangle
def area(rect):
    x1_bottom, y1_bottom, x1_top, y1_top = rect
    return (x1_top - x1_bottom)*(y1_top - y1_bottom)

def IOU(rect1, rect2):
    # Extract coordinates of rectangles
    x1_bottom, y1_bottom, x1_top, y1_top = rect1
    x2_bottom, y2_bottom, x2_top, y2_top = rect2

    # Find intersection coordinates
    x_intersection_min = max(x1_bottom, x2_bottom)
    y_intersection_min = max(y1_bottom, y2_bottom)
    x_intersection_max = min(x1_top, x2_top)
    y_intersection_max = min(y1_top, y2_top)

    # Calculate width and height of intersection
    intersection_width = max(0, x_intersection_max - x_intersection_min)
    intersection_height = max(0, y_intersection_max - y_intersection_min)

    # Calculate area of intersection
    intersection_area = intersection_width * intersection_height
    return 100*intersection_area**2/(area(rect1)*area(rect2))
'''
Main script file for starting the Phase 1 and Phase 2 algorithms 

This file was created for the UGA THINC Lab. 
Credit goes to
Divyam Mehta(dvm33231@uga.edu) for writing the code for the YOLO v8 model, Slope Tracker and Velocity Tracker.
Algorithms were also modified from:
Adrian Rosebrock, Simple Object Tracking with OpenCV, https://pyimagesearch.com/2018/07/23/simple-object-tracking-with-opencv/, accessed on 22 Feburary 2022

'''
# Testing purposes: To run type
# python3 -m AR.THINC-AR.python_files.phase_2.main.py

import os
import time
from re import A
import shutil
import pygame
from collections import OrderedDict
import cv2
import numpy as np
from functions import *
from vars import *
from mapping import *
from ultralytics import YOLO

# from SlopeTracker import SlopeTracker                  # Needs working on co-linear onion cases
# from CentroidTracker import CentroidTracker          # Most stable but only works at extremely lower speeds
from vel_tracker import VelocityTracker              # Best one but requires constant inference time for yolo between 2 frames

from pathlib import Path
path = Path(os.path.realpath (__file__))
PACKAGE_PATH = path.parent.parent.parent.parent.absolute()
model = YOLO(f'{PACKAGE_PATH}\\runs\\detect\\train9\\weights\\best.pt')

yolo = YOLO()
ct = VelocityTracker()           # Use any 1 of the 3 available Trackers

# Cleans temporary database for testing each run
shutil.rmtree(TEMP_DB)
os.mkdir(TEMP_DB)

# Cleans permanent database for testing each run
shutil.rmtree(GOOD_ONION_DB)
shutil.rmtree(BAD_ONION_DB)
os.mkdir(GOOD_ONION_DB)
os.mkdir(BAD_ONION_DB)

pygame.init()


RED = (255, 0, 0)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Video capture of cameras
ant_cap = cv2.VideoCapture(0)  # (1)  #  Camera from where onion enters
# post_cap = ant_cap
post_cap = cv2.VideoCapture(2)  #  Camera from where onion exits

# FPS of both the cameras
ant_fps = ant_cap.get(cv2.CAP_PROP_FPS)
post_fps = post_cap.get(cv2.CAP_PROP_FPS)

print("FPS of anterior camera:  " + str(ant_fps))
print("FPS of posterior camera:  " + str(post_fps))

ant_res_width = ant_cap.get(cv2.CAP_PROP_FRAME_WIDTH)
ant_res_height = ant_cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

post_res_width = post_cap.get(cv2.CAP_PROP_FRAME_WIDTH)
post_res_height = post_cap.get(cv2.CAP_PROP_FRAME_HEIGHT)


print("Frame res of Anterior camera:  " + str(ant_res_width) + "x" + str(ant_res_height))
print("Frame res of Posterior camera:  " + str(post_res_width) + "x" + str(post_res_height))


frames_processed = 0

screen = pygame.display.set_mode((1980, 1080))      # Equal to Laptop's Screen Resolution

# # Set the caption of the screen
pygame.display.set_caption('Game')

# # Fill the background colour to the screen
screen.fill(background_color)

pre_time = time.time()


# Main loop for capturing video
while True:

    pygame.event.get()
    screen.fill((0, 0, 0))

    ant_ret, ant_frame = ant_cap.read()
    post_ret, post_frame = post_cap.read()


    if ant_ret == False or post_ret == False:
        break

    ant_frame_process = ant_frame.copy()
    post_frame_process = post_frame.copy()

    # Rotate image
    ant_frame_process = cv2.rotate(ant_frame_process, cv2.ROTATE_90_CLOCKWISE)
    post_frame_process = cv2.rotate(post_frame_process, cv2.ROTATE_90_CLOCKWISE)

    # Crop the image to only contain the Conveyor Area
    ant_frame_process = ant_frame_process[270:450, 80:400]        # Original => [270:450, 80:] 
    post_frame_process = post_frame_process[270:450, 50:370]      # Original => [270:450, :370]
    # [Top:Bottom, Left:Right]
    
    # Normalization of resolution across cameras (not needed when both cameras are same)
    ant_frame_process = cv2.resize(ant_frame_process, RESIZE_RES)     
    post_frame_process = cv2.resize(post_frame_process, RESIZE_RES)   

    # Combination of frames into one video 
    process_frame = np.concatenate((post_frame_process, ant_frame_process), axis=1)    # When Anterior camera is on Right and Posterior camera is on Left

    # Resize the display_img to fit the pygame screen
    display_img = cv2.resize(process_frame, (screen.get_width(), screen.get_height()))
    
    # Process frame without any further modifications
    pure_process_frame = process_frame.copy()

    rectangles = []
    global objects
    objects = OrderedDict()


    # # YOLO detection ******************************
    if frames_processed % 1 == 0:

        # # Start time
        # start_time = time.time()

        post_time = time.time()
        time_diff = post_time - pre_time

        np_img = np.array(pure_process_frame)
        results = model(np_img, show=False)

        pre_time = post_time

        # # End time
        # end_time = time.time()

        # # Calculate and print inference time
        # inference_time = end_time - start_time
        # print("="*20)
        # print(f"Inference time: {inference_time:.4f} seconds")
        # print("="*20)

        print()
        print("="*20)
        print("Net Time Difference:  ", time_diff, " seconds")
        print("="*20)
        print()
       
        det = results[0].boxes
        
        bbox_list = []

             

        # Check IOU and neglect the onions with less confidence
        onion_list = det.xyxy

        neglect_list = []
            
        for i in range(len(onion_list)):
            for j in range(i+1, len(onion_list)):
                if IOU(onion_list[i], onion_list[j]) > 90:
                    if det.conf[i] > det.conf[j]:
                        neglect_list.append(j)

                    else:
                        neglect_list.append(i)

        xyxy_list = list(det.xyxy)
        class_list = list(det.cls)
        
        for (num, confidence) in enumerate(list(det.conf)):
            
            if (num not in neglect_list) and ((int(class_list[num]) == 0 and float(confidence) >= 0.4) or (int(class_list[num]) == 1 and float(confidence) >= 0.4)):
                
                tlx = xyxy_list[num][0]
                tly = xyxy_list[num][1]
                brx = xyxy_list[num][2]
                bry = xyxy_list[num][3]

                centx = int((tlx + brx) / 2)
                centy = int((tly + bry) / 2)

                radius = (brx - tlx) / 2

                cls = class_list[num]

                bbox_list.append((centx, centy, radius, cls, confidence))

                rectangles.append(xyxy_list[num])

                centers.append((centx, centy))

                boxes.append((round(float(tlx)), round(float(tly)), round(float(brx)), round(float(bry))))

                # Displays BBox on frame
                cv2.rectangle(process_frame, (round(float(tlx)), round(float(tly))), (round(float(brx)), round(float(bry))), (0, 255, 0), 2)


        objects = ct.update(rectangles)

        for (id, cent) in objects.items():
            print("Id:  ", id, "  |  X:  ", cent[0],   "  |  Y:  ", cent[1])
            print("Time Difference:  ", time_diff)

        # Match onions detected and classified through YOLO with tracking algorithm
        for yolo_centr in bbox_list:
            yolo_x = yolo_centr[0]
            yolo_y = yolo_centr[1]
            classification = yolo_centr[3]
            conf = yolo_centr[4]
            print("YOLO classification:" + str(int(classification)))

            for (objectId, tracker_centr) in objects.items():
                tracked_x = tracker_centr[0]
                tracked_y = tracker_centr[1]
                # if tracked_x < projectorPixelStart:
                    #print("here")
                    # If YOLO detected onion and tracked onion are the same, add a classification to ID
                
                if ((yolo_x - CENTER_LEEWAY <= tracked_x) and (yolo_x + CENTER_LEEWAY >= tracked_x) and
                    (yolo_y - CENTER_LEEWAY <= tracked_y) and (yolo_y + CENTER_LEEWAY >= tracked_y)):
                    id_class[objectId] = int(classification)

    # # END YOLO DETECTION  ******************************

    
    for (objectId, centroid) in objects.items():

        if objectId not in all_ids:
            all_ids.append(objectId)

        # Displays info on output frame
        text = "ID {}".format(objectId)
        cv2.putText(process_frame, text, (centroid[0] - 10, centroid[1] - 10),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        #if objectId in id_class:
            #if id_class[objectId] == 1:
        cv2.circle(process_frame, (centroid[0], centroid[1]), 4, (0, 255, 0), -1)
        #pygame.draw.circle(screen, (0, 255, 0), (centroid), 5)
            #else:
            #    cv2.circle(process_frame, (centroid[0], centroid[1]), 4, (0, 0, 255), -1)


    tempInd = 0

    # place in other loop to save performance
    for (objectID, centroid) in objects.items():
        # if objectID not in onionIDs:

        camX = centroid[0]
        camY = centroid[1]

        mmX, mmY, mmZ = pixelToMM(camX, camY)
        # print("Centroid -> World (mm) : ", " |   X - ", mmX, "  |   Y - ", mmY, "  |   Z - ", mmZ)
        # print("mmX", mmX)
        # print("mmY", mmY)
        
        projX, projY, projZ = mmToPixelProjector(mmX, mmY) #mmX, mmY
        # print("World -> Projector : ", " |   Proj_X - ", projX, "  |   Proj_Y - ", projY)
        # print()

        # print("ProjX ", projX)
        # print("ProjY", projY)

        
        # Make sure to make calibrate the real world co-ordinates to camera and pygame/projector in "mapping.py"
        shift_x = 0 # Leftwards   (Not Required)   
        shift_y = 0 # Downwards   (Not Required)    
       
        if objectID in id_class.keys():
            
            proj_radius = 40
            
            if id_class[objectID] == 1:
                pygame.draw.circle(screen, (0, 255, 0), (projX - shift_x, projY - shift_y), proj_radius)

            if id_class[objectID] == 0:
                pygame.draw.circle(screen, (255, 0, 0), (projX - shift_x, projY - shift_y), proj_radius)
                pygame.draw.line(screen, (255, 255, 255), (projX - proj_radius - shift_x, projY - proj_radius - shift_y), (projX + proj_radius - shift_x, projY + proj_radius - shift_y), 10)
                pygame.draw.line(screen, (255, 255, 255), (projX + proj_radius - shift_x, projY - proj_radius - shift_y), (projX - proj_radius - shift_x, projY + proj_radius - shift_y), 10)


    # For calibration testing
    # pygame.draw.circle(screen, (0, 0, 255), (1920, 1080), 75)
    pygame.draw.circle(screen, (255, 255, 255), (300,300), 25)
    # pygame.draw.circle(screen, (0, 255, 0), (0, 1080), 75)
    # pygame.draw.circle(screen, (0, 255, 0), (1920, 0), 75)

    
    
    flipped_screen = pygame.transform.flip(screen, True, True)
    screen.blit(flipped_screen, (0, 0))
    pygame.display.flip()

    # Takes image and stores time ID'd onion passed anterior camera line
    anterior_check(objects, frames_processed, pure_process_frame)

    # Finds out if an ID'd onion passed the posterior camera line
    posterior_check(objects)

    # Determines whether onions are good or bad
    good_or_bad(frames_processed)

    
    # Sorts good/bad onions to database every ten frames
    if frames_processed % 10 == 0:
        sort()      


    display_img = process_frame.copy()

    cv2.line(display_img, ANT_LINE_START, ANT_LINE_END, (255, 0, 0), 1)    # Blue Line
    cv2.line(display_img, POST_LINE_START, POST_LINE_END, (0, 255, 0), 1)  # Green Line
    
    cv2.imshow("Onion Tracking Program", display_img)

    key = cv2.waitKey(1)
    if key == ord('q'):
        break


    frames_processed = frames_processed + 1
    
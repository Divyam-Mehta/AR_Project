"""
Stores global variable information for the aglorithms to rely on and communicate with each other.

Contents:
File Paths
Camera Variables
Image Variables
ID and Tracking Variables

"""
import numpy as np

# ***** FILE PATHS *****

from pathlib import Path
import os
path = Path(os.path.realpath (__file__))
DATABASE = path.parent.parent.parent.absolute()
# print(DATABASE)

# Where onion images are stored
GOOD_ONION_DB = f'{DATABASE}\\database\\good'
BAD_ONION_DB = f'{DATABASE}\\database\\bad'
TEMP_DB = f'{DATABASE}\\database\\temp'

# ***********


# ***** CAMERA VARIABLES *****

# **********

# ***** IMAGE VARIABLES *****

# **********

# ***** ID AND TRACKING VARIABLES *****

# **********

# FPS
FRAMES_PER_SECOND = 30

# Distance between the cameras, in terms of frames (time)
CAM_DIST = 10 #100

# How long til onions disappear from tracking, in frames
DISAPPEAR_TIME = 10

# Conveyor Velocity     --->    (Velocity Tracker)
vel = np.array([-118, 0])           # Calibrate using CentroidTracker by printing onion coordinates between successive frames and taking vel average

# Angle of Conveyor in Webcam (radians)     --->    (Onion Tracker)
theta = 0                 # Calibrate using CentroidTracker by printing onion coordinates between successive frames and taking slope average
epsilon = 15*np.pi/180    # 15 degree error tolerance

# Resolutions of cameras
ANT_X_RES = 640
ANT_Y_RES = 480
POST_X_RES = 640
ANT_Y_RES = 480
PROJ_X_RES = 1920
PROJ_Y_RES = 1080

# Resized resolution for processing
RESIZE_X = 640
RESIZE_Y = 360
RESIZE_RES = (RESIZE_X, RESIZE_Y)

# Pixel leeway for tracking around lines
X_LEEWAY = 30
Y_LEEWAY = 30
CENTER_LEEWAY = 5    # 10
# 8

# Ant and Post lines to start tracking
ANT_LINE_X = 900
ANT_LINE_START = (ANT_LINE_X, 0)
ANT_LINE_END = (ANT_LINE_X, RESIZE_Y)
POST_LINE_X = 250
POST_LINE_START = (POST_LINE_X, 0)
POST_LINE_END = (POST_LINE_X, RESIZE_Y)

# Scaling factors
xCamInches = 33.5
camNormalizedPixels = RESIZE_X / xCamInches # 640 pixels per 33.5 inches
xProjInches = 20.5
projNormalizedPixels = PROJ_X_RES / xProjInches # 1920 pixels per 20.5 inches

# HSV Values of onions
low_H = 0
low_S = 0
low_V = 180
hi_H = 255
hi_S = 255
hi_V = 255


# Stores center 
centers = []
boxes = []

# Stores radii
radii = []

# Stores all ids that are detected
all_ids = []
post_ids = []
good_ids = []
bad_ids = []

# Stores times tied to ID
ant_times = {}

# Calibration required or not
calibration_required = False

# Dict value that stores ID with classification
id_class = {}

# Black background for projector
background_color = (0, 0, 0)

# Camera calibration
mtx = np.load(f'{DATABASE}\\calibration_files\\calibration_files\\cam_matrix.npy')
dist_calibration = np.load(f'{DATABASE}\\calibration_files\\calibration_files\\dist.npy')

# Pixel value from camera that projector starts
projectorPixelStart = 600   # 600
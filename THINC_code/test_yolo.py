# from ultralytics import YOLO
# from ultralytics.yolo.v8.detect.predict import DetectionPredictor
import cv2
import numpy as np
import time
from ultralytics import YOLO

model = YOLO('C:\\Users\\dvmeh\\OneDrive\\Desktop\\OnionYV8\\Divyam\\runs\\detect\\train9\\weights\\best.pt')

# Numpy Image

# while True:

#     vid_cap = cv2.VideoCapture(0)
#     vid_ret, vid_frame = vid_cap.read()

#     process_frame = np.array(vid_frame)

#     results = model(process_frame, show=True)

#     for result in results:
#         boxes = result.boxes  # Boxes object for bbox outputs
#         masks = result.masks  # Masks object for segmentation masks outputs
#         keypoints = result.keypoints  # Keypoints object for pose outputs
#         probs = result.probs  # Probs object for classification outputs

#     print(results)


#================================================================================================


# Camera
results = model.track(source="1", show=True, tracker="bytetrack.yaml", conf=0.3, iou=0.5) #results = model(source="0", show=True)

# Process results generator
for result in results:
    boxes = result.boxes  # Boxes object for bbox outputs
    masks = result.masks  # Masks object for segmentation masks outputs
    keypoints = result.keypoints  # Keypoints object for pose outputs
    probs = result.probs  # Probs object for classification outputs

print(results)


#================================================================================================
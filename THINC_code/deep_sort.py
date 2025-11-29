import os
import random
import cv2
import numpy as np
from pathlib import Path

from deep_sort.tracker import Tracker
from deep_sort.detection import Detection
from deep_sort.nn_matching import NearestNeighborDistanceMetric  

from ultralytics import YOLO


os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

path = Path(os.path.realpath (__file__))
yolov8_dir = path.parent.parent.parent.absolute()

video_path = f'{yolov8_dir}\\deep_sort\\data\\people.mp4'

cap = cv2.VideoCapture(video_path)

ret, frame = cap.read()

model = YOLO('yolov8n.pt')

# Create a metric instance
metric = NearestNeighborDistanceMetric(metric='cosine', matching_threshold=0.2, budget=100)  # Adjust parameters as needed

# Initialize the Tracker with the metric
tracker = Tracker(metric=metric)

colors = [(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)) for j in range(10)]

while ret:

    results = model(frame)
    
    for result in results:
        detections = []
        for r in result.boxes.data.tolist():
            x1, y1, x2, y2, score, class_id = r
            # x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
            # x1 = int(x1)
            # y1 = int(y1)
            # x2 = int(x2)
            # y2 = int(y2)

            # Create a bounding box and feature
            bbox = np.array([x1, y1, x2 - x1, y2 - y1], dtype=np.float32)  # Convert to [x, y, w, h] format
            confidence = float(score)  # Make sure score is a float
            feature = np.array([])  # Feature vector can be empty or extracted if available
            class_name = str(int(class_id))  # Convert class_id to a string to use as class_name
            
            # Create a Detection object
            detection = Detection(bbox, confidence, class_name, feature)
            detections.append(detection)

    tracker.update(detections)

    for track in tracker.tracks:
        bbox = track.bbox
        x1, y1, x2, y2 = bbox
        x1 = int(x1)
        y1 = int(y1)
        x2 = int(x2)
        y2 = int(y2)
        track_id = track.track_id

        cv2.rectangle(frame, (x1, y1), (x2, y2), (colors[track_id % len(colors)]), 3)

    cv2.imshow('Frame', frame)
    cv2.waitKey(1)

    ret, frame = cap.read()

cap.release()
cv2.destroyAllWindows()
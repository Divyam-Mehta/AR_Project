# AR-Based Onion Quality Inspection & Sorting System

## 🎥 Test Video

![Demo Video](media/AR_Real_Farm_1.gif)

This repository contains the code for an **Augmented Reality–based onion inspection system** developed at the **THINC Lab, University of Georgia**.

The system:

- Tracks onions moving on a **high-speed conveyor** using fused data from **two standard webcams**.
- Uses a **YOLO-v8 model** to detect onions and classify them as *good* or *blemished*.
- Uses a **custom slope- and/or velocity-based tracker** to estimate onion motion in real time.
- Projects **red (bad) or green (good) indicators** directly onto each onion using a **short-throw projector**, creating an AR overlay synchronized with the conveyor.

---

## ✨ Key Features

- **Dual-camera fusion** (anterior & posterior views).
- **YOLO-v8–based blemish detection** using a custom-trained model.
- **Multiple tracking backends**:
  - `VelocityTracker` (default, best for high-speed belts),
  - `SlopeTracker`,
  - `CentroidTracker`.
- **Real-time AR projection** using Pygame + short-throw projector.
- **Coordinate mapping** from camera pixels → real-world mm → projector pixels.
- **Automatic dataset logging** of good/bad onions for offline analysis.

---

## 📁 Project Structure

From the repository root:

```text
AR_Project/
└── THINC_code/
    ├── CentroidTracker.py       # Baseline centroid-only tracker
    ├── SlopeTracker.py          # Tracker using trajectory slope info
    ├── vel_tracker.py           # Velocity-based tracker (default)
    ├── deep_sort.py             # Optional tracker (in development)
    ├── iou.py                   # IoU utilities for overlapping detections
    ├── functions.py             # Sorting, DB operations, helper utilities
    ├── mapping.py               # Camera ↔ world ↔ projector mapping logic
    ├── vars.py                  # Global constants & configuration
    ├── onion.py                 # Onion-related data structures (if used)
    ├── test_yolo.py             # YOLO model sanity check script
    ├── rough.py                 # Experimental / sandbox code
    ├── bytetrack.yaml           # Tracker config (if using ByteTrack-style logic)
    ├── main.py                  # 🔥 Main runtime: detection + tracking + AR

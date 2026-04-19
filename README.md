# Ai_Aimbot

A high-performance, modular computer vision system designed for real-time target detection and tracking.

## Overview

Ai_Aimbot is a Python-based project that combines fast screen capturing with YOLOv8 object detection and humanized mouse control. It is designed to be efficient, undetectable, and highly customizable.

### Key Modules

- **Screen Capture (`screen_capture.py`)**: A highly optimized module using `mss` to capture a specific Region of Interest (ROI) at the center of the screen at high frame rates (supporting 60+ FPS on native hardware).
- **YOLOv8 Detection (`detector.py`)**: Wraps the `ultralytics` YOLOv8 model to detect specific targets (e.g., the 'person' class) and calculate their relative distance from the center of the screen.
- **Async Mouse Control (`mouse_controller.py`)**: Provides asynchronous, non-blocking mouse movement using `win32api`. Features human-like smoothing with jitter and interpolation to bypass simple heuristic detection.
- **Visual Debug (`debug.py`)**: A diagnostic tool that provides a real-time overlay window with bounding boxes, FOV radius indicators, and tracking mathematics.

## Requirements

The project requires Python 3.x and the following libraries:

- `mss`: For fast screen capturing.
- `numpy`: For numerical computations and image representation.
- `opencv-python`: For image processing and visual debugging.
- `ultralytics`: For YOLOv8 object detection.
- `pywin32`: For low-level Windows API access (mouse control).

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/YOUR_USERNAME/Ai_Aimbot.git
   cd Ai_Aimbot
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Continuous Detection & Movement
(Integration script coming soon)

### Visual Debug Mode
To verify the detection and tracking logic visually:
```bash
python debug.py
```

### Performance Benchmarking
To test the screen capture speed:
```bash
python benchmark.py
```

## Disclaimer
This project is for educational and research purposes only. Use it responsibly and in accordance with the terms of service of any software or games you interact with.

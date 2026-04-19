"""
detector.py
-----------
YOLOv8 Object Detection Module for AI Aimbot.

Takes a NumPy BGR frame (from screen_capture.py), runs inference filtered
to the 'person' class (class index 0), and returns the delta (ΔX, ΔY)
from the frame center to the closest detected target's bounding box center.
"""

import math
import numpy as np
from ultralytics import YOLO


class ObjectDetector:
    """
    Wraps a YOLOv8 model for efficient person detection on screen captures.

    Args:
        model_path (str): Path to YOLOv8 weights (.pt file).
                          Defaults to 'yolov8n.pt' (nano) which is auto-downloaded.
        frame_size (tuple[int, int]): (width, height) of the captured frame.
                                      Used to calculate the center of the screen.
        conf_threshold (float): Minimum confidence score to accept a detection.
    """

    # COCO class index for 'person'
    PERSON_CLASS_ID = 0

    def __init__(
        self,
        model_path: str = "yolov8n.pt",
        frame_size: tuple = (400, 400),
        conf_threshold: float = 0.4,
    ):
        self.model = YOLO(model_path)
        self.conf_threshold = conf_threshold

        # Cache frame center once — avoids recalculating every frame
        self.frame_cx = frame_size[0] / 2.0
        self.frame_cy = frame_size[1] / 2.0

        print(f"[#] ObjectDetector loaded: {model_path}")
        print(f"[#] Frame center: ({self.frame_cx}, {self.frame_cy})")
        print(f"[#] Confidence threshold: {self.conf_threshold}")

    def detect(self, frame: np.ndarray) -> dict | None:
        """
        Runs YOLOv8 inference on a BGR NumPy frame and returns the target
        closest to the frame center.

        Args:
            frame (np.ndarray): A BGR image as a NumPy array (H, W, 3).

        Returns:
            dict | None: A dict with keys:
                - 'dx'  (float): Horizontal delta from frame center to target center.
                                 Negative = target is to the left.
                - 'dy'  (float): Vertical delta from frame center to target center.
                                 Negative = target is above center.
                - 'cx'  (int):   Absolute X pixel of the target center within the frame.
                - 'cy'  (int):   Absolute Y pixel of the target center within the frame.
                - 'conf'(float): Confidence score of the detection.
            Returns None if no person is detected.
        """
        if frame is None:
            return None

        # Run inference:
        # - classes=[0]   → only detect 'person', skips all other class heads
        # - conf=...       → minimum confidence filter
        # - verbose=False  → suppress per-frame console output
        results = self.model.predict(
            frame,
            classes=[self.PERSON_CLASS_ID],
            conf=self.conf_threshold,
            verbose=False,
        )

        # results is a list; [0] is always present for a single image input
        boxes = results[0].boxes

        if boxes is None or len(boxes) == 0:
            return None

        return self._find_closest(boxes)

    def _find_closest(self, boxes) -> dict | None:
        """
        Finds the bounding box whose center is closest to the frame center.

        Args:
            boxes: ultralytics Boxes object from a Results instance.

        Returns:
            dict with dx, dy, cx, cy, conf — or None if boxes is empty.
        """
        best_dist = float("inf")
        best_result = None

        # .xyxy returns a tensor of shape (N, 4): [x1, y1, x2, y2]
        # .conf  returns a tensor of shape (N,)
        for box, conf in zip(boxes.xyxy, boxes.conf):
            x1, y1, x2, y2 = box.tolist()

            # Compute bounding box center
            cx = (x1 + x2) / 2.0
            cy = (y1 + y2) / 2.0

            # Euclidean distance from frame center to bbox center
            dist = math.hypot(cx - self.frame_cx, cy - self.frame_cy)

            if dist < best_dist:
                best_dist = dist
                best_result = {
                    "dx":   cx - self.frame_cx,
                    "dy":   cy - self.frame_cy,
                    "cx":   int(cx),
                    "cy":   int(cy),
                    "conf": float(conf),
                }

        return best_result


# ---------------------------------------------------------------------------
# Self-contained test harness
# Run:  python "c:/Users/onion/3D Objects/AI_Aimbot-Pubg/detector.py"
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import time
    import sys
    import os

    # Allow importing screen_capture from the same directory
    sys.path.insert(0, os.path.dirname(__file__))
    from screen_capture import ScreenCapture

    FRAME_W, FRAME_H = 400, 400
    TEST_DURATION_SEC = 30  # Run for 30 seconds, then auto-exit

    cap = ScreenCapture(FRAME_W, FRAME_H)
    detector = ObjectDetector(
        model_path="yolov8n.pt",
        frame_size=(FRAME_W, FRAME_H),
        conf_threshold=0.4,
    )

    print("\n[#] Live detection test started.")
    print(f"[#] Will run for {TEST_DURATION_SEC}s. Press Ctrl+C to stop early.\n")

    start = time.perf_counter()
    frame_count = 0
    detection_count = 0

    try:
        while True:
            elapsed = time.perf_counter() - start
            if elapsed >= TEST_DURATION_SEC:
                break

            frame = cap.capture()
            result = detector.detect(frame)
            frame_count += 1

            if result:
                detection_count += 1
                dx, dy = result["dx"], result["dy"]
                cx, cy = result["cx"], result["cy"]
                conf = result["conf"]
                print(
                    f"[>] Target  cx={cx:>4}  cy={cy:>4}  "
                    f"dx={dx:>+8.2f}  dy={dy:>+8.2f}  "
                    f"conf={conf:.2f}  "
                    f"FPS={frame_count / elapsed:>6.1f}"
                )
            else:
                print(
                    f"[--] No target detected  "
                    f"FPS={frame_count / elapsed:>6.1f}"
                )

    except KeyboardInterrupt:
        print("\n[#] Stopped by user.")
    finally:
        cap.close()
        elapsed = time.perf_counter() - start
        print(
            f"\n[#] Summary: {frame_count} frames in {elapsed:.1f}s "
            f"({frame_count/elapsed:.1f} FPS avg), "
            f"{detection_count} detections."
        )

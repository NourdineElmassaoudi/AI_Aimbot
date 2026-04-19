"""
debug.py
--------
Visual Verification Loop for AI Aimbot.

Ties together ScreenCapture + ObjectDetector with a real-time OpenCV
overlay window showing:
  - Green bounding boxes around every detected person
  - Red bounding box on the closest in-FOV target
  - Red FOV circle drawn at the frame center
  - Console output of (dx, dy) tracking math

Mouse controller push is disabled — overlay only.

Run:
    python "c:/Users/onion/3D Objects/AI_Aimbot-Pubg/debug.py"

Press 'q' in the 'AI Debug' window to quit.
"""

import time
import math
import cv2
import numpy as np

from screen_capture import ScreenCapture
from detector import ObjectDetector
# from mouse_controller import MouseController  # Disabled for visual debug

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
FRAME_W     = 400
FRAME_H     = 400
FOV_RADIUS  = 150      # Must match mouse_controller.FOV_RADIUS

# Overlay colours (BGR)
COLOR_BOX_DEFAULT  = (0, 255, 0)    # Green  — all detected persons
COLOR_BOX_TARGET   = (0, 0, 255)    # Red    — closest in-FOV target
COLOR_FOV_CIRCLE   = (0, 0, 255)    # Red    — FOV boundary ring
COLOR_HUD          = (255, 255, 255) # White  — HUD text

FONT       = cv2.FONT_HERSHEY_SIMPLEX
FONT_SCALE = 0.45
FONT_THICK = 1

# Frame center (constant for a fixed ROI)
CENTER_X = FRAME_W // 2
CENTER_Y = FRAME_H // 2


def in_fov(dx: float, dy: float) -> bool:
    return math.hypot(dx, dy) <= FOV_RADIUS


def draw_overlay(frame: np.ndarray, results, closest_idx: int) -> np.ndarray:
    """
    Draw all bounding boxes and the FOV circle onto `frame`.

    Parameters
    ----------
    frame        : BGR numpy array (H, W, 3)
    results      : ultralytics Results object (results[0] from model.predict)
    closest_idx  : index of the closest in-FOV box, or -1 if none
    """
    # --- FOV circle ---
    cv2.circle(
        frame,
        (CENTER_X, CENTER_Y),
        FOV_RADIUS,
        COLOR_FOV_CIRCLE,
        thickness=1,
        lineType=cv2.LINE_AA,
    )
    # Small crosshair at center
    cv2.drawMarker(
        frame,
        (CENTER_X, CENTER_Y),
        COLOR_FOV_CIRCLE,
        markerType=cv2.MARKER_CROSS,
        markerSize=10,
        thickness=1,
        line_type=cv2.LINE_AA,
    )

    if results is None:
        return frame

    boxes = results.boxes
    if boxes is None or len(boxes) == 0:
        return frame

    for idx, (box, conf) in enumerate(zip(boxes.xyxy, boxes.conf)):
        x1, y1, x2, y2 = map(int, box.tolist())
        color = COLOR_BOX_TARGET if idx == closest_idx else COLOR_BOX_DEFAULT

        # Bounding box
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

        # Confidence label
        label = f"{float(conf):.2f}"
        cv2.putText(
            frame, label,
            (x1, max(y1 - 4, 0)),
            FONT, FONT_SCALE, color, FONT_THICK,
            cv2.LINE_AA,
        )

    return frame


def draw_hud(frame: np.ndarray, fps: float, target: dict | None) -> np.ndarray:
    """Draw a minimal HUD (FPS + target status) at the top-left corner."""
    lines = [
        f"FPS: {fps:.1f}",
        f"FOV: {FOV_RADIUS}px",
    ]
    if target:
        lines += [
            f"dx: {target['dx']:+.1f}",
            f"dy: {target['dy']:+.1f}",
            f"conf: {target['conf']:.2f}",
        ]
    else:
        lines.append("Target: None")

    for i, line in enumerate(lines):
        y = 16 + i * 16
        cv2.putText(
            frame, line,
            (6, y),
            FONT, FONT_SCALE, COLOR_HUD, FONT_THICK,
            cv2.LINE_AA,
        )
    return frame


def find_closest_idx(results, frame_cx: float, frame_cy: float) -> tuple[int, dict | None]:
    """
    Find the index of the bounding box closest to the frame center
    that is also within FOV_RADIUS.

    Returns (closest_idx, target_dict) or (-1, None).
    """
    if results is None or results.boxes is None or len(results.boxes) == 0:
        return -1, None

    best_dist = float("inf")
    best_idx  = -1
    best_data = None

    for idx, (box, conf) in enumerate(zip(results.boxes.xyxy, results.boxes.conf)):
        x1, y1, x2, y2 = box.tolist()
        cx = (x1 + x2) / 2.0
        cy = (y1 + y2) / 2.0
        dx = cx - frame_cx
        dy = cy - frame_cy

        if not in_fov(dx, dy):
            continue

        dist = math.hypot(dx, dy)
        if dist < best_dist:
            best_dist = dist
            best_idx  = idx
            best_data = {
                "dx":   dx,
                "dy":   dy,
                "cx":   int(cx),
                "cy":   int(cy),
                "conf": float(conf),
            }

    return best_idx, best_data


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    cap      = ScreenCapture(FRAME_W, FRAME_H)
    detector = ObjectDetector(
        model_path="yolov8n.pt",
        frame_size=(FRAME_W, FRAME_H),
        conf_threshold=0.4,
    )

    # Disabled: controller = MouseController(); controller.start()

    print("[#] Visual debug started. Press 'q' in 'AI Debug' window to quit.\n")

    # FPS tracking
    prev_time   = time.perf_counter()
    frame_count = 0
    fps         = 0.0

    while True:
        raw_frame = cap.capture()
        if raw_frame is None:
            continue

        # Run YOLO inference — returns the raw Results object for drawing
        raw_results = detector.model.predict(
            raw_frame,
            classes=[ObjectDetector.PERSON_CLASS_ID],
            conf=detector.conf_threshold,
            verbose=False,
        )
        yolo_result = raw_results[0] if raw_results else None

        # Find the closest in-FOV target
        closest_idx, target = find_closest_idx(yolo_result, CENTER_X, CENTER_Y)

        # Console output — tracking math (mouse controller disabled)
        if target:
            print(
                f"[>] dx={target['dx']:>+8.2f}  dy={target['dy']:>+8.2f}  "
                f"cx={target['cx']:>4}  cy={target['cy']:>4}  "
                f"conf={target['conf']:.2f}  FPS={fps:.1f}"
                # controller.push(target["dx"], target["dy"])  # DISABLED
            )
        else:
            print(f"[--] No target in FOV  FPS={fps:.1f}")

        # --- Draw overlays on a copy so the overlay never corrupts input ---
        display = raw_frame.copy()
        display = draw_overlay(display, yolo_result, closest_idx)
        display = draw_hud(display, fps, target)

        cv2.imshow("AI Debug", display)

        # FPS calculation
        frame_count += 1
        now = time.perf_counter()
        if now - prev_time >= 0.5:           # Update every 0.5s
            fps = frame_count / (now - prev_time)
            frame_count = 0
            prev_time = now

        # Press 'q' to quit
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.close()
    cv2.destroyAllWindows()
    # controller.stop()  # DISABLED
    print("[#] Debug session ended.")

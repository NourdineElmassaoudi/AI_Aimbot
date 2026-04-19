"""
mouse_controller.py
-------------------
Async, queue-driven mouse controller for AI Aimbot.

Runs in a background daemon thread. The main YOLO detection loop pushes
target deltas (dx, dy) via push(). The worker thread consumes them,
applies humanized interpolation, and fires raw win32api mouse events.

Usage:
    from mouse_controller import MouseController

    controller = MouseController()
    controller.start()

    # From your detection loop:
    if result:
        controller.push(result["dx"], result["dy"])

    # On exit:
    controller.stop()
"""

import math
import queue
import random
import threading
import time

import win32api
import win32con

# ---------------------------------------------------------------------------
# Tunable constants — adjust to taste without touching class internals
# ---------------------------------------------------------------------------
FOV_RADIUS   = 150    # px — targets beyond this radius are ignored
STEPS        = 12     # interpolation steps per move
DURATION_MS  = 60     # total time budget (ms) for one complete move
JITTER_PX    = 1.5    # max random noise (±) per axis per step


class MouseController:
    """
    Async, thread-safe mouse controller with humanized movement.

    Parameters
    ----------
    fov_radius : int
        Maximum pixel radius from frame center for a target to be acted on.
    steps : int
        Number of micro-steps to split each movement into.
    duration_ms : int
        Wall-clock time budget (ms) for completing one full movement.
    jitter_px : float
        Maximum random displacement (pixels) added per axis per step.
    """

    def __init__(
        self,
        fov_radius: int   = FOV_RADIUS,
        steps: int        = STEPS,
        duration_ms: int  = DURATION_MS,
        jitter_px: float  = JITTER_PX,
    ):
        self.fov_radius   = fov_radius
        self.steps        = steps
        self.duration_ms  = duration_ms
        self.jitter_px    = jitter_px

        # Pre-compute per-step sleep once — avoids computing inside hot loop
        self._step_sleep = duration_ms / steps / 1000.0

        # maxsize=1: only the freshest target matters; old ones are discarded
        self._queue = queue.Queue(maxsize=1)

        # Signals the worker thread to exit cleanly
        self._stop_event = threading.Event()

        # Daemon thread: auto-killed when main process exits
        self._thread = threading.Thread(
            target=self._worker,
            name="MouseControllerThread",
            daemon=True,
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def start(self):
        """Start the background worker thread."""
        self._thread.start()
        print(
            f"[#] MouseController started  "
            f"FOV={self.fov_radius}px  steps={self.steps}  "
            f"duration={self.duration_ms}ms  jitter=±{self.jitter_px}px"
        )

    def stop(self):
        """Signal the worker thread to stop and wait for it to exit."""
        self._stop_event.set()
        self._thread.join(timeout=1.0)
        print("[#] MouseController stopped.")

    def push(self, dx: float, dy: float):
        """
        Push a new target delta to the queue.

        Non-blocking: if the queue already holds an unprocessed target,
        it is discarded and replaced with the new one. This ensures the
        background thread always acts on the most recent detection.

        Parameters
        ----------
        dx : float  Horizontal delta (pixels) — right is positive.
        dy : float  Vertical delta (pixels)   — down is positive.
        """
        try:
            # Drain the stale item first, then add the fresh one
            try:
                self._queue.get_nowait()
            except queue.Empty:
                pass
            self._queue.put_nowait((dx, dy))
        except queue.Full:
            pass  # Should never reach this after the drain, but be safe

    def in_fov(self, dx: float, dy: float) -> bool:
        """Return True if (dx, dy) is within the configured FOV radius."""
        return math.hypot(dx, dy) <= self.fov_radius

    # ------------------------------------------------------------------
    # Internal worker
    # ------------------------------------------------------------------

    def _worker(self):
        """Background thread: block on queue, then move mouse on new target."""
        while not self._stop_event.is_set():
            try:
                # Block for up to 50 ms, then loop to re-check stop_event
                dx, dy = self._queue.get(timeout=0.05)
            except queue.Empty:
                continue

            if not self.in_fov(dx, dy):
                print(f"[--] Outside FOV ({math.hypot(dx, dy):.1f}px > {self.fov_radius}px), skipping.")
                continue

            self._smooth_move(dx, dy)

    def _smooth_move(self, total_dx: float, total_dy: float):
        """
        Move the mouse from its current position by (total_dx, total_dy)
        in a series of humanized micro-steps.

        Design:
        - Divides total delta evenly across `self.steps` steps.
        - Adds independent ±jitter_px noise to each axis every step.
        - Accumulates integer rounding remainders and flushes them on the
          last step so the total displacement is always exact.
        - Sleeps `_step_sleep` seconds between steps — single call,
          no busy-wait, CPU-friendly on i5 4th Gen.
        """
        step_dx = total_dx / self.steps
        step_dy = total_dy / self.steps

        # Remainder accumulators for sub-pixel precision
        acc_x = 0.0
        acc_y = 0.0

        for i in range(self.steps):
            is_last = (i == self.steps - 1)

            if is_last:
                # Flush accumulated remainder on the final step
                raw_x = step_dx + acc_x
                raw_y = step_dy + acc_y
            else:
                # Add humanizing jitter — different each step
                jx = random.uniform(-self.jitter_px, self.jitter_px)
                jy = random.uniform(-self.jitter_px, self.jitter_px)
                raw_x = step_dx + jx
                raw_y = step_dy + jy

            # Convert to integers for the win32 call
            int_x = int(raw_x)
            int_y = int(raw_y)

            # Track sub-pixel remainder to re-add next iteration
            if not is_last:
                acc_x += (raw_x - int_x)
                acc_y += (raw_y - int_y)

            # Fire raw relative hardware mouse event
            win32api.mouse_event(
                win32con.MOUSEEVENTF_MOVE,
                int_x,
                int_y,
                0,
                0,
            )

            # CPU-friendly sleep — no busy-waiting
            time.sleep(self._step_sleep)


# ---------------------------------------------------------------------------
# Self-contained test harness
# Run:  python "c:/Users/onion/3D Objects/AI_Aimbot-Pubg/mouse_controller.py"
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=== MouseController Self-Test ===\n")

    ctrl = MouseController(
        fov_radius=150,
        steps=12,
        duration_ms=60,
        jitter_px=1.5,
    )
    ctrl.start()

    tests = [
        ("Move right  +100px  [PASS expected]",  100,   0),
        ("Move left   -100px  [PASS expected]", -100,   0),
        ("Move down   +80px   [PASS expected]",    0,  80),
        ("Move up     -80px   [PASS expected]",    0, -80),
        ("FOV reject  +500px  [SKIP expected]",  500,   0),
    ]

    for label, dx, dy in tests:
        print(f"\n[>] {label}  →  push({dx}, {dy})")
        ctrl.push(dx, dy)
        # Wait long enough for the movement to fully complete
        time.sleep((ctrl.duration_ms / 1000) + 0.1)

    ctrl.stop()
    print("\n=== Test complete ===")

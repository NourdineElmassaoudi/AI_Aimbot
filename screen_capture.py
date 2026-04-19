import mss
import numpy as np
import time
import cv2

class ScreenCapture:
    """
    Highly optimized screen capture module using mss for high-frequency frame acquisition.
    Designed for performance-critical applications like AI computer vision.
    """
    def __init__(self, width=400, height=400):
        self.sct = mss.mss()
        
        # Select the primary monitor (index 1)
        # monitors[0] is the span of all monitors
        monitor = self.sct.monitors[1]
        
        # Calculate the center of the screen
        screen_width = monitor["width"]
        screen_height = monitor["height"]
        
        left = (screen_width - width) // 2
        top = (screen_height - height) // 2
        
        # ROI definition for mss.grab
        self.region = {
            "top": top,
            "left": left,
            "width": width,
            "height": height,
            "mon": 1
        }
        
        # Cache dimensions for reshapes
        self.width = width
        self.height = height
        
        print(f"[#] ScreenCapture Initialized: {screen_width}x{screen_height}")
        print(f"[#] ROI: {width}x{height} centered at ({left}, {top})")

    def capture(self):
        """
        Grabs a frame from the screen and returns it as a BGR NumPy array.
        Optimized to use raw memory buffers and avoid unnecessary copies.
        """
        try:
            # Grab the screen data (raw pixels)
            sct_img = self.sct.grab(self.region)
            
            # Convert to numpy array via buffer (extremely fast)
            # mss outputs BGRA by default. We reshape and slice for BGR.
            frame = np.frombuffer(sct_img.bgra, dtype=np.uint8)
            frame.shape = (self.height, self.width, 4)
            
            # Drop the alpha channel to return BGR format for OpenCV
            return frame[:, :, :3]
        except Exception as e:
            print(f"[!] Capture Error: {e}")
            return None

    def close(self):
        self.sct.close()

if __name__ == "__main__":
    # Initialize with 400x400 ROI as per requirements
    cap = ScreenCapture(400, 400)
    
    print("[#] Starting High-Performance FPS Loop...")
    print("[#] Press Ctrl+C to terminate.")
    
    # Use perf_counter for high-precision timing
    start_time = time.perf_counter()
    frame_count = 0
    
    try:
        while True:
            frame = cap.capture()
            
            if frame is not None:
                frame_count += 1
            
            # Calculate and display FPS every 100 frames to reduce console overhead
            if frame_count % 100 == 0:
                elapsed = time.perf_counter() - start_time
                fps = frame_count / elapsed
                print(f"\rCurrent FPS: {fps:.2f}", end="", flush=True)
                
            # Optional: Minimal delay to prevent 100% CPU usage if needed
            # For max FPS, we keep it as tight as possible.
            
    except KeyboardInterrupt:
        print("\n\n[#] Performance test stopped by user.")
    finally:
        cap.close()
        print("[#] Resources released.")

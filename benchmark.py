import mss
import time
import numpy as np

sct = mss.mss()
monitor = sct.monitors[1]
region = {"top": 300, "left": 400, "width": 400, "height": 400}

# Warmup
for _ in range(10):
    sct.grab(region)

print("Starting benchmark...")

# Test 1: Just Grab
start = time.time()
for _ in range(100):
    sct.grab(region)
print(f"Just Grab: {100 / (time.time() - start):.2f} FPS")

# Test 2: Grab + bgra property
start = time.time()
for _ in range(100):
    sct.grab(region).bgra
print(f"Grab + .bgra: {100 / (time.time() - start):.2f} FPS")

# Test 3: Grab + np.frombuffer(bgra).reshape
start = time.time()
for _ in range(100):
    img = np.frombuffer(sct.grab(region).bgra, dtype=np.uint8).reshape(400, 400, 4)
print(f"Grab + np.frombuffer + reshape: {100 / (time.time() - start):.2f} FPS")

# Test 4: Grab + np.frombuffer + reshape + slice
start = time.time()
for _ in range(100):
    img = np.frombuffer(sct.grab(region).bgra, dtype=np.uint8).reshape(400, 400, 4)[:,:,:3]
print(f"Grab + np.frombuffer + reshape + slice: {100 / (time.time() - start):.2f} FPS")

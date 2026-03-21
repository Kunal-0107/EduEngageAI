import sounddevice as sd
import numpy as np
import time

def print_volume(indata, frames, time, status):
    if status:
        print(f"Status: {status}")
    # Calculate volume
    volume_norm = np.linalg.norm(indata) * 10
    print(f"|{'#' * int(volume_norm * 100)}  ({volume_norm:.4f})")

print("------------------------------------------------")
print("AUDIO DIAGNOSTIC TOOL")
print("------------------------------------------------")

# We will try the most likely devices from your list:
# 1 = Intel Array (MME)
# 2 = Brio 100 (MME)
# 14 = Brio 100 (WASAPI - Higher Quality)
# 15 = Intel Array (WASAPI - Higher Quality)

test_devices = [2, 14, 1, 15] 

for device_id in test_devices:
    print(f"\n>>> TESTING DEVICE ID: {device_id} <<<")
    try:
        # Try to open the stream
        with sd.InputStream(device=device_id, callback=print_volume):
            print(f"Listening on Device {device_id}... SPEAK NOW!")
            sd.sleep(4000) # Listen for 4 seconds
            print("Finished testing this device.\n")
    except Exception as e:
        print(f"FAILED to open Device {device_id}: {e}")

print("------------------------------------------------")
print("TEST COMPLETE. Which device showed hash marks (####)?")
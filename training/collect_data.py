import cv2
import mediapipe as mp
import numpy as np
import csv
import os
import time

# Setup MediaPipe
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils

# File to save data
if not os.path.exists('training'): os.makedirs('training')
data_file = 'training/engagement_data.csv'

# Initialize CSV Headers
if not os.path.exists(data_file):
    with open(data_file, mode='w', newline='') as f:
        writer = csv.writer(f)
        headers = ['class']
        for i in range(33):
            headers += [f'x{i}', f'y{i}', f'z{i}', f'v{i}']
        writer.writerow(headers)

# --- SMART CAMERA OPENER ---
# --- SMART CAMERA OPENER ---
print("Attempting to open Camera 0...")
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # <--- Added cv2.CAP_DSHOW

if not cap.isOpened():
    print("Camera 0 failed. Attempting to open Camera 1...")
    cap = cv2.VideoCapture(1, cv2.CAP_DSHOW) # <--- Added cv2.CAP_DSHOW here too

if not cap.isOpened():
    print("CRITICAL ERROR: Could not open ANY camera.")
    print("1. Close Zoom/Teams/Discord.")
    print("2. Check if your privacy settings allow Python to access the camera.")
    exit()

print("=== CAMERA OPENED SUCCESSFULLY ===")
print("=== DATA COLLECTION STARTED ===")
print("INSTRUCTIONS:")
print("1. Click on the POPUP WINDOW (Video Feed).")
print("2. Press and HOLD '1' key while acting ENGAGED.")
print("3. Press and HOLD '0' key while acting DISTRACTED.")
print("4. Press 'q' to Quit.")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Error: Camera stopped sending frames.")
        break

    # Convert to RGB
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(image)
    
    # Draw landmarks
    if results.pose_landmarks:
        mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

    # UI Overlay
    cv2.putText(frame, "Hold '1': Engaged | Hold '0': Distracted", (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    cv2.imshow('Data Collector', frame)
    
    k = cv2.waitKey(1)
    if k == ord('q'):
        break
    
    # RECORD DATA
    if results.pose_landmarks and (k == ord('1') or k == ord('0')):
        row = []
        label = 1 if k == ord('1') else 0
        row.append(label)
        
        for lm in results.pose_landmarks.landmark:
            row.append(lm.x)
            row.append(lm.y)
            row.append(lm.z)
            row.append(lm.visibility)
            
        with open(data_file, mode='a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(row)
        
        status = "RECORDING: ENGAGED" if label == 1 else "RECORDING: DISTRACTED"
        print(status)

cap.release()
cv2.destroyAllWindows()
import cv2
import mediapipe as mp
import numpy as np
import tensorflow as tf
import os

class EngagementAnalyzer:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        
        # Load Model
        model_path = 'models/custom_engagement_model.h5'
        if os.path.exists(model_path):
            self.model = tf.keras.models.load_model(model_path)
            self.model_loaded = True
            print("AI Model Loaded Successfully.")
        else:
            self.model_loaded = False
            print("WARNING: Model not found. Running in demo mode (random scores).")

    def analyze_frame(self, frame):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(frame_rgb)
        
        score = 0.5 # Default neutral
        
        if results.pose_landmarks:
            # Draw Skeleton
            mp.solutions.drawing_utils.draw_landmarks(
                frame, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)
            
            if self.model_loaded:
                # Prepare data for AI
                row = []
                for lm in results.pose_landmarks.landmark:
                    row.append(lm.x)
                    row.append(lm.y)
                    row.append(lm.z)
                    row.append(lm.visibility)
                
                # Predict
                X = np.array([row])
                prediction = self.model.predict(X, verbose=0)
                score = float(prediction[0][0])
        
        return frame, score
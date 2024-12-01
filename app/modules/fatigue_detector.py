# app/modules/fatigue_detector.py

import os
import cv2
import dlib
import logging
from scipy.spatial import distance as dist
from definition import DATASET_MODEL_DIR
import numpy as np
import mediapipe as mp
import time

# Load face detector and facial landmarks predictor
face_detector = dlib.get_frontal_face_detector()
landmark_predictor = dlib.shape_predictor(os.path.join(DATASET_MODEL_DIR, "shape_predictor_68_face_landmarks.dat"))
logger = logging.getLogger(__name__)

class FatigueDetector:
    def __init__(self):
        # Initialize MediaPipe Face Mesh
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_drawing = mp.solutions.drawing_utils
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Initialize metrics
        self.blink_counter = 0
        self.frame_counter = 0
        self.last_blink_time = time.time()
        self.eye_closed_time = 0
        self.eye_closed_start = None
        self.blink_rate = 0
        self.eye_closure_duration = 0
        self.head_position = "Forward"
        
        # Constants
        self.EYE_AR_THRESH = 0.25
        self.EYE_AR_CONSEC_FRAMES = 3
        
        # Eye landmarks indices
        self.LEFT_EYE = [362, 385, 387, 263, 373, 380]
        self.RIGHT_EYE = [33, 160, 158, 133, 153, 144]
        
        # Head pose landmarks
        self.HEAD_POSE_POINTS = [33, 263, 1, 61, 291, 199]

    def process_frame(self, frame):
        frame_metrics = {
            "blink_rate": 0,
            "eye_closure_duration": 0,
            "head_position": "Forward",
            "alertness": 100
        }
        
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process the frame and get face landmarks
        results = self.face_mesh.process(rgb_frame)
        
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                # Get metrics
                eye_state = self._check_eye_state(face_landmarks)
                head_pose = self._get_head_pose(face_landmarks, frame)
                
                # Draw landmarks and annotations
                self._draw_landmarks(frame, face_landmarks, eye_state)
                
                # Update metrics
                frame_metrics = self._update_metrics(eye_state, head_pose)
        
        return frame, frame_metrics
    
    def _calculate_ear(self, eye_points, face_landmarks):
        """Calculate Eye Aspect Ratio"""
        points = []
        for point in eye_points:
            points.append([
                face_landmarks.landmark[point].x,
                face_landmarks.landmark[point].y
            ])
        
        # Calculate vertical distances
        A = dist.euclidean(points[1], points[5])
        B = dist.euclidean(points[2], points[4])
        
        # Calculate horizontal distance
        C = dist.euclidean(points[0], points[3])
        
        # Calculate EAR
        ear = (A + B) / (2.0 * C)
        return ear

    def _check_eye_state(self, landmarks):
        left_ear = self._calculate_ear(self.LEFT_EYE, landmarks)
        right_ear = self._calculate_ear(self.RIGHT_EYE, landmarks)
        
        avg_ear = (left_ear + right_ear) / 2.0
        
        if avg_ear < self.EYE_AR_THRESH:
            if self.eye_closed_start is None:
                self.eye_closed_start = time.time()
            return "closed"
        else:
            if self.eye_closed_start is not None:
                self.eye_closed_time = time.time() - self.eye_closed_start
                if self.eye_closed_time > 0.15:  # Longer than a typical blink
                    self.blink_counter += 1
                self.eye_closed_start = None
            return "open"

    def _get_head_pose(self, landmarks, frame):
        """Estimate head pose"""
        face_points = []
        for point in self.HEAD_POSE_POINTS:
            x = int(landmarks.landmark[point].x * frame.shape[1])
            y = int(landmarks.landmark[point].y * frame.shape[0])
            face_points.append([x, y])
        
        face_points = np.array(face_points, dtype=np.float32)
        
        # Calculate head rotation using face points
        if len(face_points) > 0:
            # Simple head position estimation based on face points
            left_right_diff = abs(face_points[0][0] - face_points[1][0])
            if left_right_diff < frame.shape[1] * 0.2:
                return "Forward"
            elif face_points[0][0] > face_points[1][0]:
                return "Right"
            else:
                return "Left"
        return "Unknown"

    def _draw_landmarks(self, frame, landmarks, eye_state):
        # Draw face mesh
        self.mp_drawing.draw_landmarks(
            image=frame,
            landmark_list=landmarks,
            connections=self.mp_face_mesh.FACEMESH_TESSELATION,
            landmark_drawing_spec=None,
            connection_drawing_spec=self.mp_drawing.DrawingSpec(
                color=(0, 255, 0), thickness=1, circle_radius=1
            )
        )
        
        # Draw eye state
        cv2.putText(
            frame,
            f"Eyes: {eye_state}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0) if eye_state == "open" else (0, 0, 255),
            2
        )

    def _update_metrics(self, eye_state, head_pose):
        current_time = time.time()
        time_diff = current_time - self.last_blink_time
        
        # Update blink rate (blinks per minute)
        if time_diff >= 60:
            self.blink_rate = self.blink_counter
            self.blink_counter = 0
            self.last_blink_time = current_time
        
        # Update head position
        self.head_position = head_pose
        
        # Calculate alertness
        alertness = self._calculate_alertness(eye_state, head_pose)
        
        return {
            "blink_rate": self.blink_rate,
            "eye_closure_duration": round(self.eye_closure_duration, 2),
            "head_position": self.head_position,
            "alertness": alertness
        }

    def _calculate_alertness(self, eye_state, head_pose):
        """Calculate alertness percentage based on various factors"""
        alertness = 100
        
        # Reduce alertness for closed eyes
        if eye_state == "closed":
            alertness -= 30
        
        # Reduce alertness for non-forward head position
        if head_pose != "Forward":
            alertness -= 20
        
        # Reduce alertness for abnormal blink rate
        if self.blink_rate < 10 or self.blink_rate > 30:
            alertness -= 15
        
        # Ensure alertness stays within 0-100
        return max(0, min(100, alertness))


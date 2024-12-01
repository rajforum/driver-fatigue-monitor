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
from datetime import datetime, timedelta
from collections import deque

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
        
        # Store blink history
        self.blink_times = deque(maxlen=100)  # Store last 100 blinks
        self.last_blink_state = False
        
        # Store eye closure history
        self.eye_closure_start = None
        self.eye_closure_durations = deque(maxlen=10)  # Store last 10 closure durations
        
        # Store head position history
        self.head_positions = deque(maxlen=10)  # Store last 10 positions
        
        # EAR (Eye Aspect Ratio) threshold
        self.EAR_THRESHOLD = 0.2
        
        # Enhanced yawning tracking
        self.yawn_times = deque(maxlen=100)
        self.yawn_durations = deque(maxlen=10)  # Store last 10 yawn durations
        self.last_yawn_state = False
        self.yawn_start_time = None
        self.MAR_THRESHOLD = 1.0
        self.MIN_YAWN_DURATION = 1.0  # Minimum duration (seconds) to consider as yawn
        self.mouth_landmarks = [
            48, 54,  # Outer mouth corners (left, right)
            51, 57,  # Top and bottom of the outer lips (center points)
            60, 64,  # Inner mouth corners (left, right)
            62, 66   # Top and bottom of the inner lips (center points)
        ]
        
        # [
        #     61, 291,  # Outer mouth corners
        #     0, 17,    # Top and bottom outer lip
        #     405, 314, # Inner mouth corners
        #     178, 152  # Top and bottom inner lip
        # ]

    def process_frame(self, frame):
        """Process a frame and return processed frame with metrics"""
        try:
            # Convert to RGB for MediaPipe
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.face_mesh.process(rgb_frame)
            
            metrics = {
                'blink_rate': 0,
                'eye_closure_duration': 0,
                'head_position': 'Unknown',
                'yawn_count': 0,
                'alertness': 100
            }
            
            if results.multi_face_landmarks:
                face_landmarks = results.multi_face_landmarks[0]
                
                # Process eye metrics
                left_ear = self._get_ear(face_landmarks, "left")
                right_ear = self._get_ear(face_landmarks, "right")
                avg_ear = (left_ear + right_ear) / 2
                
                # Detect blink
                if avg_ear < self.EAR_THRESHOLD and not self.last_blink_state:
                    self.blink_times.append(datetime.now())
                    self.last_blink_state = True
                elif avg_ear >= self.EAR_THRESHOLD:
                    self.last_blink_state = False
                
                # Track eye closure
                if avg_ear < self.EAR_THRESHOLD:
                    if not self.eye_closure_start:
                        self.eye_closure_start = datetime.now()
                elif self.eye_closure_start:
                    duration = (datetime.now() - self.eye_closure_start).total_seconds()
                    self.eye_closure_durations.append(duration)
                    self.eye_closure_start = None
                
                # Get head position
                head_pos = self._get_head_position(face_landmarks)
                self.head_positions.append(head_pos)
                
                # Enhanced mouth metrics processing
                mar = self._get_mar(face_landmarks)
                
                # More sophisticated yawn detection with duration
                if mar > self.MAR_THRESHOLD:
                    if not self.last_yawn_state:
                        self.yawn_start_time = datetime.now()
                        self.last_yawn_state = True
                elif self.last_yawn_state:
                    if self.yawn_start_time:
                        yawn_duration = (datetime.now() - self.yawn_start_time).total_seconds()
                        if yawn_duration >= self.MIN_YAWN_DURATION:
                            self.yawn_times.append(datetime.now())
                            self.yawn_durations.append(yawn_duration)
                    self.last_yawn_state = False
                    self.yawn_start_time = None
                
                # Update metrics with enhanced yawn data
                metrics = {
                    'blink_rate': self.get_blink_count(),
                    'eye_closure_duration': self.get_eye_closure_duration(),
                    'head_position': self.get_head_position(),
                    'yawn_count': self.get_yawn_count(),
                    'yawn_duration': self.get_average_yawn_duration(),
                    'current_mar': mar,
                    'is_yawning': self.last_yawn_state,
                    'alertness': self._calculate_alertness(avg_ear, mar)
                }
                
                # Draw facial landmarks with mouth visualization
                self._draw_face_mesh(frame, face_landmarks, draw_mouth=False) #Disable draw mouth
            
            return frame, metrics
            
        except Exception as e:
            logger.error(f"Error processing frame: {str(e)}")
            return frame, metrics

    def get_blink_count(self):
        """Get number of blinks in the last minute"""
        try:
            one_minute_ago = datetime.now() - timedelta(minutes=1)
            recent_blinks = [t for t in self.blink_times if t > one_minute_ago]
            return len(recent_blinks)
        except Exception as e:
            logger.error(f"Error getting blink count: {str(e)}")
            return 0

    def get_eye_closure_duration(self):
        """Get average eye closure duration"""
        try:
            if self.eye_closure_durations:
                return sum(self.eye_closure_durations) / len(self.eye_closure_durations)
            return 0.0
        except Exception as e:
            logger.error(f"Error getting eye closure duration: {str(e)}")
            return 0.0

    def get_head_position(self):
        """Get most common recent head position"""
        try:
            if self.head_positions:
                # Return most common position from recent history
                from collections import Counter
                position_counts = Counter(self.head_positions)
                return position_counts.most_common(1)[0][0]
            return 'Centered'
        except Exception as e:
            logger.error(f"Error getting head position: {str(e)}")
            return 'Centered'

    def get_yawn_count(self):
        """Get number of yawns in the last minute"""
        try:
            one_minute_ago = datetime.now() - timedelta(minutes=1)
            recent_yawns = [t for t in self.yawn_times if t > one_minute_ago]
            return len(recent_yawns)
        except Exception as e:
            logger.error(f"Error getting yawn count: {str(e)}")
            return 0

    def get_average_yawn_duration(self):
        """Get average yawn duration in seconds"""
        try:
            if self.yawn_durations:
                return sum(self.yawn_durations) / len(self.yawn_durations)
            return 0.0
        except Exception as e:
            logger.error(f"Error getting average yawn duration: {str(e)}")
            return 0.0

    def _get_ear(self, landmarks, eye):
        """Calculate Eye Aspect Ratio"""
        try:
            if eye == "left":
                pts = [33, 160, 158, 133, 153, 144]  # Left eye landmarks
            else:
                pts = [362, 385, 387, 263, 373, 380]  # Right eye landmarks
            
            # Get landmark points
            points = [landmarks.landmark[pt] for pt in pts]
            
            # Calculate EAR
            A = self._distance(points[1], points[5])
            B = self._distance(points[2], points[4])
            C = self._distance(points[0], points[3])
            
            ear = (A + B) / (2.0 * C)
            return ear
        except Exception as e:
            logger.error(f"Error calculating EAR: {str(e)}")
            return 0.3

    def _distance(self, p1, p2):
        """Calculate Euclidean distance between two points"""
        return ((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2) ** 0.5

    def _get_head_position(self, landmarks):
        """Enhanced head position detection using multiple facial landmarks"""
        try:
            # Use multiple landmarks for more accurate position detection
            # Nose tip (1), chin (152), left eye outer (33), right eye outer (263)
            # left ear (234), right ear (454)
            key_points = {
                'nose': landmarks.landmark[1],
                'chin': landmarks.landmark[152],
                'left_eye': landmarks.landmark[33],
                'right_eye': landmarks.landmark[263],
                'left_ear': landmarks.landmark[234],
                'right_ear': landmarks.landmark[454]
            }

            # Calculate head rotation
            # Left-right rotation (yaw)
            left_right_ratio = abs(key_points['left_ear'].x - key_points['nose'].x) / \
                              abs(key_points['right_ear'].x - key_points['nose'].x)
            
            # Up-down rotation (pitch)
            nose_chin_dist = abs(key_points['nose'].y - key_points['chin'].y)
            eye_level = (key_points['left_eye'].y + key_points['right_eye'].y) / 2
            vertical_ratio = (key_points['nose'].y - eye_level) / nose_chin_dist

            # Define thresholds
            YAW_THRESHOLD = 0.2  # Threshold for left-right rotation
            PITCH_THRESHOLD = 0.15  # Threshold for up-down rotation

            # Determine position
            if abs(1 - left_right_ratio) > YAW_THRESHOLD:
                if left_right_ratio > 1:
                    return 'Right'
                else:
                    return 'Left'
            elif abs(vertical_ratio) > PITCH_THRESHOLD:
                if vertical_ratio > 0:
                    return 'Down'
                else:
                    return 'Up'
            
            # Additional check for extreme positions
            nose_x = key_points['nose'].x
            if nose_x < 0.35:
                return 'Far Left'
            elif nose_x > 0.65:
                return 'Far Right'

            return 'Centered'

        except Exception as e:
            logger.error(f"Error getting head position: {str(e)}")
            return 'Centered'

    def _get_mar(self, landmarks):
        """Calculate Mouth Aspect Ratio"""
        try:
            # Mouth landmarks
            mouth_pts = self.mouth_landmarks
            
            # Get landmark points
            points = [landmarks.landmark[pt] for pt in mouth_pts]
            
            # Calculate MAR
            A = self._distance(points[0], points[1])  # Mouth width
            B = self._distance(points[2], points[3])  # Outer height
            C = self._distance(points[4], points[5])  # Inner width
            D = self._distance(points[6], points[7])  # Inner height
            
            mar = (B + D) / (2.0 * A-C)
            return mar
        except Exception as e:
            logger.error(f"Error calculating MAR: {str(e)}")
            return 0.0

    def _calculate_alertness(self, ear, mar):
        """Enhanced alertness calculation including yawn metrics"""
        try:
            score = 100
            
            # Reduce score based on eye closure
            if ear < self.EAR_THRESHOLD:
                score -= 30
            
            # Reduce score based on blink rate
            blink_rate = self.get_blink_count()
            if blink_rate < 10:  # Too few blinks
                score -= 20
            elif blink_rate > 30:  # Too many blinks
                score -= 30
            
            # Enhanced yawn-based reduction
            yawn_count = self.get_yawn_count()
            avg_yawn_duration = self.get_average_yawn_duration()
            
            if yawn_count > 3:
                score -= 25
            elif yawn_count > 1:
                score -= 15
            
            # Additional reduction for long yawns
            if avg_yawn_duration > 4.0:  # Very long yawns
                score -= 20
            elif avg_yawn_duration > 2.5:  # Moderately long yawns
                score -= 10
            
            # Reduce score based on head position
            if self.get_head_position() != 'Centered':
                score -= 20
            
            return max(0, min(100, score))
        except Exception as e:
            logger.error(f"Error calculating alertness: {str(e)}")
            return 100

    def _draw_face_mesh(self, frame, landmarks, draw_mouth=True):
        """Draw face mesh with enhanced visualization including head position"""
        try:
            h, w, _ = frame.shape
            
            # Draw general landmarks
            for landmark in landmarks.landmark:
                x = int(landmark.x * w)
                y = int(landmark.y * h)
                cv2.circle(frame, (x, y), 1, (0, 255, 0), -1)
            
            # Draw head position indicators
            head_pos = self._get_head_position(landmarks)
            position_color = {
                'Centered': (0, 255, 0),
                'Left': (0, 165, 255),
                'Right': (0, 165, 255),
                'Up': (0, 165, 255),
                'Down': (0, 0, 255),
                'Far Left': (0, 0, 255),
                'Far Right': (0, 0, 255)
            }.get(head_pos, (0, 255, 0))

            # Draw head position text
            cv2.putText(frame, f"Head: {head_pos}", (10, 90),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, position_color, 2)

            # Draw direction arrow based on head position
            center_x, center_y = w // 2, 30
            arrow_length = 30
            if head_pos in ['Left', 'Far Left']:
                cv2.arrowedLine(frame, (center_x, center_y), 
                              (center_x - arrow_length, center_y), 
                              position_color, 2)
            elif head_pos in ['Right', 'Far Right']:
                cv2.arrowedLine(frame, (center_x, center_y), 
                              (center_x + arrow_length, center_y), 
                              position_color, 2)
            elif head_pos == 'Up':
                cv2.arrowedLine(frame, (center_x, center_y), 
                              (center_x, center_y - arrow_length), 
                              position_color, 2)
            elif head_pos == 'Down':
                cv2.arrowedLine(frame, (center_x, center_y), 
                              (center_x, center_y + arrow_length), 
                              position_color, 2)

            if draw_mouth:
                # Draw mouth landmarks and connections
                mouth_points = [landmarks.landmark[pt] for pt in self.mouth_landmarks]
                mouth_coords = [(int(pt.x * w), int(pt.y * h)) for pt in mouth_points]
                
                # Draw mouth outline
                color = (0, 0, 255) if self.last_yawn_state else (0, 255, 0)
                thickness = 2 if self.last_yawn_state else 1
                
                # Draw outer mouth
                cv2.line(frame, mouth_coords[0], mouth_coords[1], color, thickness)  # Corners
                cv2.line(frame, mouth_coords[0], mouth_coords[2], color, thickness)  # Top
                cv2.line(frame, mouth_coords[1], mouth_coords[3], color, thickness)  # Bottom
                
                # Draw inner mouth
                cv2.line(frame, mouth_coords[4], mouth_coords[5], color, thickness)  # Inner corners
                cv2.line(frame, mouth_coords[4], mouth_coords[6], color, thickness)  # Inner top
                cv2.line(frame, mouth_coords[5], mouth_coords[7], color, thickness)  # Inner bottom
                
                # Add MAR value display
                mar = self._get_mar(landmarks)
                cv2.putText(frame, f"MAR: {mar:.2f}", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                
                # Add yawn status
                if self.last_yawn_state:
                    duration = (datetime.now() - self.yawn_start_time).total_seconds()
                    cv2.putText(frame, f"YAWNING: {duration:.1f}s", (10, 60),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                
        except Exception as e:
            logger.error(f"Error drawing face mesh: {str(e)}")


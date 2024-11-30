# app/modules/data_processing.py

import os
import cv2
import dlib
import logging
from scipy.spatial import distance as dist
from app.modules.data_parameter import calculate_ear, calculate_head_tilt
from definition import DATASET_MODEL_DIR

# Load face detector and facial landmarks predictor
face_detector = dlib.get_frontal_face_detector()
landmark_predictor = dlib.shape_predictor(os.path.join(DATASET_MODEL_DIR, "shape_predictor_68_face_landmarks.dat"))
logger = logging.getLogger(__name__)

def process_frame(frame):
    logger.info("Processing frame for face and eye detection")

    try:
        # Convert frame to grayscale for detector
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect faces
        faces = face_detector(gray)

        for face in faces:
            # Draw a rectangle around the face
            cv2.rectangle(frame, (face.left(), face.top()), (face.right(), face.bottom()), (255, 0, 0), 2)
            cv2.putText(frame, "Face", (face.left(), face.top() - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

            # Get landmarks
            landmarks = landmark_predictor(gray, face)

            # Left and right eye landmarks
            left_eye = [(landmarks.part(i).x, landmarks.part(i).y) for i in range(36, 42)]
            right_eye = [(landmarks.part(i).x, landmarks.part(i).y) for i in range(42, 48)]

            # Calculate EAR and eye status
            # Calculate EAR for both eyes
            left_ear = calculate_ear(left_eye)
            right_ear = calculate_ear(right_eye)
            avg_ear = (left_ear + right_ear) / 2.0

            # EAR threshold for detecting closed eyes
            EAR_THRESHOLD = 0.25  # Adjust based on testing
            if avg_ear < EAR_THRESHOLD:
                eye_status = "Sleepy Eye"
                color = (0, 0, 255)  # Red for closed eyes
            else:
                eye_status = "Open Eye"
                color = (0, 255, 0)  # Green for open eyes

            # Draw eye landmarks and EAR status
            for (x, y) in left_eye + right_eye:
                cv2.circle(frame, (x, y), 2, color, -1)

            # Label each eye region with "Eye" and show EAR value and status
            eye_label_pos = (face.left() + 5, face.bottom() + 25)  # Position below face box for clarity
            cv2.putText(frame, f"EAR: {avg_ear:.2f}", eye_label_pos, cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
            cv2.putText(frame, eye_status, (face.left(), face.top() - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            cv2.putText(frame, "Left Eye", (left_eye[0][0], left_eye[0][1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)  # Left eye label
            cv2.putText(frame, "Right Eye", (right_eye[0][0], right_eye[0][1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)  # Right eye label

        return frame
    except Exception as e:
        logger.error(f"Error processing frame: {e}", exc_info=True)
        raise

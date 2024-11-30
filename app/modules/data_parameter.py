# app/modules/data_parameter.py

from scipy.spatial import distance as dist
import numpy as np
import logging

logger = logging.getLogger(__name__)

def calculate_ear(eye):
    logger.info("Calculating EAR eye detection")

    # Compute the euclidean distances between the two sets of vertical eye landmarks (x, y) - distances between points
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])

    # Compute the euclidean distance between the horizontal eye landmark (x, y)
    C = dist.euclidean(eye[0], eye[3])

    # Calculate the eye aspect ratio (EAR)
    ear = (A + B) / (2.0 * C)
    return ear

def calculate_head_tilt(landmarks):
    logger.info("Calculating Head Tilt")
    # Get coordinates for left eye, right eye, and nose tip
    left_eye_center = np.mean([(landmarks.part(i).x, landmarks.part(i).y) for i in range(36, 42)], axis=0)
    right_eye_center = np.mean([(landmarks.part(i).x, landmarks.part(i).y) for i in range(42, 48)], axis=0)
    nose_tip = (landmarks.part(30).x, landmarks.part(30).y)

    # Calculate the angle between the line joining the eyes and the horizontal
    dx = right_eye_center[0] - left_eye_center[0]
    dy = right_eye_center[1] - left_eye_center[1]
    angle = np.degrees(np.arctan2(dy, dx))

    # Adjust angle for readability: -10 to +10 degrees as acceptable straight position
    head_tilt = abs(angle)
    return head_tilt
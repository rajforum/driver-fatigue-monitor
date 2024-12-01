# app/modules/data_collection.py

import cv2
from flask import Response
from app.modules.fatigue_detector import FatigueDetector
from app.socket_events import update_metrics


def generate_frames():
    """Generate frames from camera for video streaming."""
    cap = cv2.VideoCapture(0)
    detector = FatigueDetector()  # Create a single detector instance
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        # Process the frame and get metrics
        processed_frame, metrics = detector.process_frame(frame)
        
        # Update and emit metrics via Socket.IO
        # update_metrics(metrics)
        
        # Convert frame to bytes
        _, buffer = cv2.imencode('.jpg', processed_frame)
        frame_bytes = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    
    cap.release()

def capture_video():
    """Return a streaming response for the camera feed."""
    return Response(
        generate_frames(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

def capture_video_old():
    """Capture video from the camera and process frames for fatigue detection."""
    # Open the video feed (or you can replace this with a video file path)
    cap = cv2.VideoCapture(0) 
    detector = FatigueDetector() 

    while cap.isOpened():
        # Capture frame-by-frame
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        # Process the frame for eye and head detection
        processed_frame = detector.process_frame(frame)

        # Display the resulting frame with labels
        cv2.imshow('Face and Eye Detection with Labels', processed_frame)

        # Break the loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the capture and close all windows
    cap.release()
    cv2.destroyAllWindows()


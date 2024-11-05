# app/modules/data_collection.py

import cv2
from app.modules.data_processing import process_frame


def capture_video():
    """Capture video from the camera and process frames for fatigue detection."""
    cap = cv2.VideoCapture(0)  # Start video capture from the default camera

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        # Process the frame for eye and head detection
        processed_frame = process_frame(frame)

        # Display the processed video feed
        cv2.imshow('Video Feed', processed_frame)

        # Break the loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    

if __name__ == "__main__":
    capture_video()

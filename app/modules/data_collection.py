# app/modules/data_collection.py

import cv2
from app.modules.data_processing import process_frame


def capture_video():
    """Capture video from the camera and process frames for fatigue detection."""
    # Open the video feed (or you can replace this with a video file path)
    cap = cv2.VideoCapture(0) 

    while cap.isOpened():
        # Capture frame-by-frame
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        # Process the frame for eye and head detection
        processed_frame = process_frame(frame)

        # Display the resulting frame with labels
        cv2.imshow('Face and Eye Detection with Labels', processed_frame)

        # Break the loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the capture and close all windows
    cap.release()
    cv2.destroyAllWindows()
    

if __name__ == "__main__":
    capture_video()

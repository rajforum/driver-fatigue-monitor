# app/modules/data_collection.py

import cv2
from app.modules.fatigue_detector import FatigueDetector
from app.services.performance import PerformanceMetrics
import logging

logger = logging.getLogger(__name__)

# Initialize performance metrics
performance_tracker = PerformanceMetrics()

def generate_frames(user_info):
    """Generate frames from camera for video streaming."""
    try:
        from app.services.service_manager import ServiceManager
        socket_service = ServiceManager.get_instance().sockets
        cap = cv2.VideoCapture(0)
        detector = FatigueDetector()
        
        while cap.isOpened():
            performance_tracker.start_processing()
            
            ret, frame = cap.read()
            if not ret:
                break
                
            processed_frame, metrics = detector.process_frame(frame)
            
            try:
                socket_service.emit_metrics(metrics, user_info)
            except Exception as e:
                logger.error(f"Error emitting metrics: {str(e)}")
            
            _, buffer = cv2.imencode('.jpg', processed_frame)
            frame_bytes = buffer.tobytes()
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            
            performance_tracker.end_processing()
        
        cap.release()
    except Exception as e:
        logger.error(f"Error in generate_frames: {str(e)}")
        if 'cap' in locals():
            cap.release()

def get_current_performance():
    """Get current performance metrics"""
    return performance_tracker.get_prf_metrics()


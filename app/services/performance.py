import time
from collections import deque
from statistics import mean
import logging

logger = logging.getLogger(__name__)

class PerformanceMetrics:
    def __init__(self, max_samples=30):
        self.frame_times = deque(maxlen=max_samples)
        self.processing_times = deque(maxlen=max_samples)
        self.last_frame_time = None
        self.processing_start_time = None

    def start_processing(self):
        """Mark the start of frame processing"""
        self.processing_start_time = time.time()
        if self.last_frame_time:
            frame_interval = self.processing_start_time - self.last_frame_time
            self.frame_times.append(frame_interval)
        self.last_frame_time = self.processing_start_time

    def end_processing(self):
        """Mark the end of frame processing"""
        if self.processing_start_time:
            processing_time = (time.time() - self.processing_start_time) * 1000  # Convert to ms
            self.processing_times.append(processing_time)
            self.processing_start_time = None

    def get_prf_metrics(self):
        """Get current performance metrics"""
        try:
            if self.frame_times:
                avg_frame_interval = mean(self.frame_times)
                current_fps = 1 / avg_frame_interval if avg_frame_interval > 0 else 0
            else:
                current_fps = 0

            avg_processing_time = mean(self.processing_times) if self.processing_times else 0

            return {
                'fps': round(current_fps, 1),
                'processingTime': round(avg_processing_time, 1),
                'frameCount': len(self.frame_times),
                'avgFrameInterval': round(mean(self.frame_times) * 1000, 1) if self.frame_times else 0
            }
        except Exception as e:
            logger.error(f"Error calculating performance metrics: {str(e)}")
            return {
                'fps': 0,
                'processingTime': 0,
                'frameCount': 0,
                'avgFrameInterval': 0
            }

    def reset(self):
        """Reset all metrics"""
        self.frame_times.clear()
        self.processing_times.clear()
        self.last_frame_time = None
        self.processing_start_time = None 
from datetime import datetime
from app.config import Config
from app.routes.fatigue import get_fitness_data
from flask import session
from google.oauth2.credentials import Credentials
import logging
from app.services.validation import MetricsValidator
from app.services.history import MetricsHistory
from app.services.alerts import AlertService
from typing import Dict
from app.services.mock_data import get_mock_metrics as get_fitbit_mock_metrics
from app.services.fitbit_client import FitbitClient

logger = logging.getLogger(__name__)

def get_mock_metrics():
    return {
        'heartRate': '72',
        'alertness': '95',
        'blinkRate': 'Normal (12/min)',
        'eyeClosure': '0.2s',
        'headPosition': 'Centered',
        'yawnCount': '0/min',
        'alertStatus': 'Normal',
        'timestamp': datetime.utcnow().isoformat()
    }

def get_real_metrics():
    """Get real metrics from Fitbit API"""
    try:
        if 'fitbit_token' not in session:
            return {'error': 'Not authenticated with Fitbit'}
        
        user_email = session.get('user_info', {}).get('email')
        if not user_email:
            return {'error': 'User email not found'}

        # Get Fitbit data
        client = FitbitClient(session['fitbit_token'])
        metrics = client.get_all_metrics()
        
        # Validate and sanitize metrics
        metrics = MetricsValidator.sanitize_metrics(metrics)
        
        # Save to history
        history = MetricsHistory()
        history.save_metrics(user_email, metrics)
        
        # Add historical averages
        averages = history.get_average_metrics(user_email)
        metrics.update({
            'historical_averages': averages
        })
        
        return metrics
    except Exception as e:
        logger.error(f"Error in get_real_metrics: {str(e)}")
        return {'error': str(e)}

def process_heart_rate(heart_rate_data):
    """Process heart rate data from Google Fit"""
    try:
        # Extract heart rate values from Google Fit response
        if 'bucket' in heart_rate_data:
            for bucket in heart_rate_data['bucket']:
                if bucket.get('dataset'):
                    for dataset in bucket['dataset']:
                        if dataset.get('point'):
                            # Get the most recent heart rate value
                            points = dataset['point']
                            if points:
                                latest_point = points[-1]  # Get most recent
                                if 'value' in latest_point:
                                    return str(int(latest_point['value'][0]['fpVal']))
        return '0'  # Return 0 if no valid heart rate found
    except Exception as e:
        logger.error(f"Error processing heart rate: {str(e)}")
        return '0'

def calculate_alertness():
    """Calculate alertness based on multiple factors"""
    try:
        # Get the required metrics
        blink_rate = float(get_blink_rate().split()[0])
        eye_closure = float(get_eye_closure().replace('s', ''))
        head_pos = get_head_position()
        yawn_count = float(get_yawn_count().split()[0])

        # Calculate alertness score (0-100)
        score = 100

        # Reduce score based on blink rate
        if blink_rate < 10:  # Too few blinks
            score -= 20
        elif blink_rate > 30:  # Too many blinks
            score -= 30

        # Reduce score based on eye closure duration
        if eye_closure > 0.3:  # Eyes closed too long
            score -= 40

        # Reduce score based on head position
        if head_pos != 'Centered':
            score -= 25

        # Reduce score based on yawning
        if yawn_count > 3:  # More than 3 yawns per minute
            score -= 25
        elif yawn_count > 1:  # 1-3 yawns per minute
            score -= 15

        # Ensure score stays within 0-100
        score = max(0, min(100, score))
        return str(score)

    except Exception as e:
        logger.error(f"Error calculating alertness: {str(e)}")
        return '0'

def get_blink_rate():
    """Get blink rate from eye detection"""
    try:
        # Get blink rate from the last few seconds of detection
        from app.modules.fatigue_detector import FatigueDetector
        detector = FatigueDetector()
        blink_count = detector.get_blink_count()  # Get blinks in last 60 seconds
        return f"{blink_count}/min"
    except Exception as e:
        logger.error(f"Error getting blink rate: {str(e)}")
        return "0/min"

def get_eye_closure():
    """Get eye closure duration"""
    try:
        # Get actual eye closure from video processing
        from app.modules.fatigue_detector import FatigueDetector
        detector = FatigueDetector()
        closure_duration = detector.get_eye_closure_duration()
        return f"{closure_duration:.1f}s"
    except Exception as e:
        logger.error(f"Error getting eye closure: {str(e)}")
        return "0.0s"

def get_head_position():
    """Get head position from video processing"""
    try:
        from app.modules.fatigue_detector import FatigueDetector
        detector = FatigueDetector()
        position = detector.get_head_position()
        return position  # Should return one of: 'Centered', 'Left', 'Right', 'Up', 'Down'
    except Exception as e:
        logger.error(f"Error getting head position: {str(e)}")
        return 'Centered'

def get_yawn_count():
    """Get yawn count from detection"""
    try:
        from app.modules.fatigue_detector import FatigueDetector
        detector = FatigueDetector()
        yawn_count = detector.get_yawn_count()
        return f"{yawn_count}/min"
    except Exception as e:
        logger.error(f"Error getting yawn count: {str(e)}")
        return "0/min"

def determine_alert_status():
    """Determine alert status based on metrics"""
    try:
        alertness = float(calculate_alertness())
        
        if alertness >= 80:
            return 'Normal'
        elif alertness >= 60:
            return 'Warning'
        else:
            return 'Danger'
    except Exception as e:
        logger.error(f"Error determining alert status: {str(e)}")
        return 'Error'

class MetricsService:
    def __init__(self):
        self.alert_service = AlertService()
        self.monitoring_active = False
        self.background_tasks = []

    def cleanup(self):
        """Clean up metrics service resources"""
        try:
            self.stop_monitoring()
            self.alert_service = None
        except Exception as e:
            logger.error(f"Error cleaning up metrics service: {str(e)}")

    def stop_monitoring(self):
        """Stop all monitoring tasks"""
        try:
            self.monitoring_active = False
            for task in self.background_tasks:
                task.cancel()
            self.background_tasks.clear()
        except Exception as e:
            logger.error(f"Error stopping monitoring: {str(e)}")

    def get_metrics(self):
        """Get metrics based on configuration"""
        if Config.USE_MOCK_DATA:
            if Config.MOCK_DATA_SOURCE == 'fitbit':
                return get_fitbit_mock_metrics()
            return get_mock_metrics()  # Original simple mock data
        return get_real_metrics() 

    def process_metrics(self, raw_metrics: Dict, user_email: str) -> Dict:
        """Process and validate metrics, generate alerts if needed"""
        try:
            # Validate metrics
            metrics = MetricsValidator.sanitize_metrics(raw_metrics)
            
            # Check for alerts
            alert_level, alert_message = self.alert_service.check_metrics(metrics, user_email)
            
            # Add alert info to metrics
            metrics.update({
                'alertLevel': alert_level,
                'alertMessage': alert_message
            })
            
            return metrics
        except Exception as e:
            logger.error(f"Error processing metrics: {str(e)}")
            return raw_metrics 
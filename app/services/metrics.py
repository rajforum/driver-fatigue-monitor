from datetime import datetime
from app.config import Config
from app.routes.fatigue import get_fitness_data
from flask import session
from google.oauth2.credentials import Credentials
import logging
from app.services.validation import MetricsValidator
from app.services.history import MetricsHistory

logger = logging.getLogger(__name__)

def get_mock_metrics():
    return {
        'heartRate': '72',
        'alertness': '95',
        'blinkRate': 'Normal (12/min)',
        'eyeClosure': '0.2s',
        'headPosition': 'Centered',
        'alertStatus': 'Normal',
        'timestamp': datetime.utcnow().isoformat()
    }

def get_real_metrics():
    try:
        if 'google_credentials' not in session:
            return {'error': 'Not authenticated'}
        
        user_email = session.get('user_info', {}).get('email')
        if not user_email:
            return {'error': 'User email not found'}

        credentials = Credentials(**session['google_credentials'])
        heart_rate_data = get_fitness_data().get_json()
        
        # Get raw metrics
        raw_metrics = {
            'heartRate': process_heart_rate(heart_rate_data),
            'alertness': calculate_alertness(),
            'blinkRate': get_blink_rate(),
            'eyeClosure': get_eye_closure(),
            'headPosition': get_head_position(),
            'alertStatus': determine_alert_status(),
            'timestamp': datetime.utcnow().isoformat()
        }

        # Validate and sanitize metrics
        metrics = MetricsValidator.sanitize_metrics(raw_metrics)
        
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
        blink_rate = float(get_blink_rate().split()[0])  # Extract numeric value
        eye_closure = float(get_eye_closure().replace('s', ''))  # Remove 's' and convert
        head_pos = get_head_position()

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

        # Ensure score stays within 0-100
        score = max(0, min(100, score))
        return str(score)

    except Exception as e:
        logger.error(f"Error calculating alertness: {str(e)}")
        return '0'

def get_blink_rate():
    """Get blink rate from eye detection"""
    try:
        # TODO: Get actual blink rate from video processing
        # For now, return mock data with some variation
        import random
        base_rate = 15
        variation = random.randint(-3, 3)
        return f"{base_rate + variation}/min"
    except Exception as e:
        logger.error(f"Error getting blink rate: {str(e)}")
        return "0/min"

def get_eye_closure():
    """Get eye closure duration"""
    try:
        # TODO: Get actual eye closure from video processing
        # For now, return mock data with some variation
        import random
        base_duration = 0.2
        variation = random.uniform(-0.1, 0.1)
        return f"{base_duration + variation:.1f}s"
    except Exception as e:
        logger.error(f"Error getting eye closure: {str(e)}")
        return "0.0s"

def get_head_position():
    # Get head position from video processing
    # TODO: Implement actual detection
    return 'Centered'

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

def get_metrics():
    """Get metrics based on configuration"""
    if Config.USE_MOCK_DATA:
        return get_mock_metrics()
    return get_real_metrics() 
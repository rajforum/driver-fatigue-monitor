from flask import Blueprint, jsonify, redirect, session, url_for
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from datetime import datetime, timedelta
from app.services.google_health import get_google_fit_data
from functools import wraps
import random
from app.config import Config
from app.services.fitbit_client import FitbitClient
import logging

fatigue_bp = Blueprint('fatigue', __name__)
logger = logging.getLogger(__name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is logged in and has valid credentials
        if 'google_credentials' not in session:
            return redirect(url_for('google_auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@fatigue_bp.route('/health_data')
@login_required
def health_data():
    credentials = Credentials(**session['google_credentials'])
    data = get_google_fit_data(credentials)
    return jsonify(data)

@fatigue_bp.route('/fitness_data')
@login_required
def get_fitness_data():
    """Get fitness data (heart rate) from Fitbit/Google Fit"""
    try:
        if Config.USE_MOCK_DATA:
            # Return mock heart rate data
            current_time = datetime.utcnow()
            mock_data = {
                'bucket': [{
                    'startTimeMillis': str(int((current_time - timedelta(hours=1)).timestamp() * 1000)),
                    'endTimeMillis': str(int(current_time.timestamp() * 1000)),
                    'dataset': [{
                        'point': [
                            {
                                'value': [{'fpVal': random.randint(60, 100)}],
                                'startTimeNanos': str(int(current_time.timestamp() * 1e9)),
                                'endTimeNanos': str(int(current_time.timestamp() * 1e9))
                            } for _ in range(60)  # One reading per minute
                        ]
                    }]
                }]
            }
            return jsonify(mock_data)

        # If using real data, check which service to use
        if 'fitbit_token' in session:
            return get_fitbit_heart_rate_data()
        elif 'google_credentials' in session:
            return get_google_fit_heart_rate_data()
        else:
            return jsonify({'error': 'No fitness service connected'}), 400

    except Exception as e:
        logger.error(f"Error getting fitness data: {str(e)}")
        return jsonify({'error': str(e)}), 500

@fatigue_bp.route('/analyze_fatigue')
@login_required
def analyze_fatigue():
    """Analyze fatigue based on combined metrics"""
    try:
        if Config.USE_MOCK_DATA:
            # Generate mock fatigue analysis
            mock_score = random.randint(60, 100)
            mock_analysis = {
                'score': mock_score,
                'level': 'Normal' if mock_score >= 80 else 'Warning' if mock_score >= 60 else 'Danger',
                'factors': {
                    'heart_rate': {
                        'value': random.randint(60, 100),
                        'status': 'normal',
                        'contribution': 0.3
                    },
                    'activity': {
                        'value': random.randint(1000, 10000),
                        'status': 'normal',
                        'contribution': 0.3
                    },
                    'sleep': {
                        'value': random.randint(5, 9),
                        'status': 'normal',
                        'contribution': 0.4
                    }
                },
                'recommendations': [
                    'Take a break every 2 hours',
                    'Stay hydrated',
                    'Maintain good posture'
                ],
                'timestamp': datetime.utcnow().isoformat()
            }
            return jsonify(mock_analysis)

        # Get real data from connected services
        heart_rate_data = get_fitness_data().get_json()
        activity_data = get_activity_data().get_json()
        sleep_data = get_sleep_data().get_json()

        # Calculate fatigue score based on all metrics
        fatigue_score = calculate_fatigue_score(heart_rate_data, activity_data, sleep_data)
        
        return jsonify(fatigue_score)

    except Exception as e:
        logger.error(f"Error analyzing fatigue: {str(e)}")
        return jsonify({'error': str(e)}), 500

@fatigue_bp.route('/sleep_data')
@login_required
def get_sleep_data():
    """Get sleep data from Fitbit/Google Fit"""
    try:
        if Config.USE_MOCK_DATA:
            # Return mock sleep data
            return jsonify({
                'sleep': [{
                    'dateOfSleep': datetime.utcnow().strftime('%Y-%m-%d'),
                    'duration': 25200000,  # 7 hours in milliseconds
                    'efficiency': 90,
                    'minutesAsleep': 420,
                    'minutesAwake': 40,
                    'timeInBed': 460,
                    'levels': {
                        'summary': {
                            'deep': {'count': 4, 'minutes': 85},
                            'light': {'count': 25, 'minutes': 249},
                            'rem': {'count': 4, 'minutes': 86},
                            'wake': {'count': 23, 'minutes': 40}
                        }
                    }
                }]
            })

        # If using real data, check which service to use
        if 'fitbit_token' in session:
            return get_fitbit_sleep_data()
        elif 'google_credentials' in session:
            return get_google_fit_sleep_data()
        else:
            return jsonify({'error': 'No fitness service connected'}), 400

    except Exception as e:
        logger.error(f"Error getting sleep data: {str(e)}")
        return jsonify({'error': str(e)}), 500

@fatigue_bp.route('/activity_data')
@login_required
def get_activity_data():
    """Get activity data from Fitbit/Google Fit"""
    try:
        if Config.USE_MOCK_DATA:
            # Return mock activity data
            return jsonify({
                'summary': {
                    'activeScore': random.randint(70, 100),
                    'activityCalories': random.randint(400, 800),
                    'caloriesOut': random.randint(1800, 2200),
                    'distances': [
                        {'activity': 'total', 'distance': random.uniform(3.0, 8.0)},
                        {'activity': 'tracker', 'distance': random.uniform(3.0, 8.0)},
                        {'activity': 'loggedActivities', 'distance': 0},
                        {'activity': 'veryActive', 'distance': random.uniform(0.5, 2.0)},
                        {'activity': 'moderatelyActive', 'distance': random.uniform(0.5, 2.0)},
                        {'activity': 'lightlyActive', 'distance': random.uniform(1.0, 4.0)},
                        {'activity': 'sedentaryActive', 'distance': 0}
                    ],
                    'fairlyActiveMinutes': random.randint(10, 30),
                    'lightlyActiveMinutes': random.randint(150, 250),
                    'sedentaryMinutes': random.randint(600, 800),
                    'steps': random.randint(5000, 12000),
                    'veryActiveMinutes': random.randint(15, 45)
                }
            })

        # If using real data, check which service to use
        if 'fitbit_token' in session:
            return get_fitbit_activity_data()
        elif 'google_credentials' in session:
            return get_google_fit_activity_data()
        else:
            return jsonify({'error': 'No fitness service connected'}), 400

    except Exception as e:
        logger.error(f"Error getting activity data: {str(e)}")
        return jsonify({'error': str(e)}), 500

def get_fitbit_sleep_data():
    """Get sleep data from Fitbit API"""
    try:
        client = FitbitClient(session['fitbit_token'])
        return jsonify(client.get_sleep_data())
    except Exception as e:
        logger.error(f"Error getting Fitbit sleep data: {str(e)}")
        return jsonify({'error': str(e)}), 500

def get_google_fit_sleep_data():
    """Get sleep data from Google Fit API"""
    try:
        credentials = Credentials(**session['google_credentials'])
        fitness_service = build('fitness', 'v1', credentials=credentials)
        
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=1)

        # Google Fit sleep data request
        # Note: This is a simplified version, you might need to adjust based on Google Fit's actual sleep data structure
        body = {
            "aggregateBy": [{
                "dataTypeName": "com.google.sleep.segment"
            }],
            "bucketByTime": {"durationMillis": 86400000},  # 24 hours
            "startTimeMillis": int(start_time.timestamp() * 1000),
            "endTimeMillis": int(end_time.timestamp() * 1000)
        }

        sleep_data = fitness_service.users().dataset().aggregate(userId="me", body=body).execute()
        return jsonify(sleep_data)
    except Exception as e:
        logger.error(f"Error getting Google Fit sleep data: {str(e)}")
        return jsonify({'error': str(e)}), 500

def get_fitbit_activity_data():
    """Get activity data from Fitbit API"""
    try:
        client = FitbitClient(session['fitbit_token'])
        return jsonify(client.get_activity_data())
    except Exception as e:
        logger.error(f"Error getting Fitbit activity data: {str(e)}")
        return jsonify({'error': str(e)}), 500

def get_google_fit_activity_data():
    """Get activity data from Google Fit API"""
    try:
        credentials = Credentials(**session['google_credentials'])
        fitness_service = build('fitness', 'v1', credentials=credentials)
        
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=1)

        body = {
            "aggregateBy": [{
                "dataTypeName": "com.google.step_count.delta"
            }, {
                "dataTypeName": "com.google.calories.expended"
            }, {
                "dataTypeName": "com.google.active_minutes"
            }],
            "bucketByTime": {"durationMillis": 86400000},  # 24 hours
            "startTimeMillis": int(start_time.timestamp() * 1000),
            "endTimeMillis": int(end_time.timestamp() * 1000)
        }

        activity_data = fitness_service.users().dataset().aggregate(userId="me", body=body).execute()
        return jsonify(activity_data)
    except Exception as e:
        logger.error(f"Error getting Google Fit activity data: {str(e)}")
        return jsonify({'error': str(e)}), 500

def get_fitbit_heart_rate_data():
    """Get heart rate data from Fitbit API"""
    try:
        client = FitbitClient(session['fitbit_token'])
        return jsonify(client.get_heart_rate_data())
    except Exception as e:
        logger.error(f"Error getting Fitbit heart rate data: {str(e)}")
        return jsonify({'error': str(e)}), 500

def get_google_fit_heart_rate_data():
    """Get heart rate data from Google Fit API"""
    try:
        credentials = Credentials(**session['google_credentials'])
        fitness_service = build('fitness', 'v1', credentials=credentials)
        
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=1)

        body = {
            "aggregateBy": [{
                "dataTypeName": "com.google.heart_rate.bpm"
            }],
            "bucketByTime": {"durationMillis": 3600000},  # 1 hour buckets
            "startTimeMillis": int(start_time.timestamp() * 1000),
            "endTimeMillis": int(end_time.timestamp() * 1000)
        }

        heart_rate_data = fitness_service.users().dataset().aggregate(userId="me", body=body).execute()
        return jsonify(heart_rate_data)
    except Exception as e:
        logger.error(f"Error getting Google Fit heart rate data: {str(e)}")
        return jsonify({'error': str(e)}), 500

def extract_current_heart_rate(heart_rate_data: dict) -> float:
    """Extract current heart rate from heart rate data"""
    try:
        if 'bucket' in heart_rate_data:
            for bucket in heart_rate_data['bucket']:
                if 'dataset' in bucket:
                    for dataset in bucket['dataset']:
                        if 'point' in dataset and dataset['point']:
                            # Get the most recent point
                            latest_point = dataset['point'][-1]
                            if 'value' in latest_point and latest_point['value']:
                                return float(latest_point['value'][0]['fpVal'])
        return 70.0  # Default value if no data found
    except Exception as e:
        logger.error(f"Error extracting heart rate: {str(e)}")
        return 70.0

def extract_activity_level(activity_data: dict) -> float:
    """Extract activity level from activity data"""
    try:
        if 'summary' in activity_data:
            summary = activity_data['summary']
            # Calculate activity score based on different activity levels
            very_active = float(summary.get('veryActiveMinutes', 0))
            fairly_active = float(summary.get('fairlyActiveMinutes', 0))
            lightly_active = float(summary.get('lightlyActiveMinutes', 0))
            
            # Weight different activity levels
            activity_score = (very_active * 1.0 + 
                            fairly_active * 0.7 + 
                            lightly_active * 0.3)
            return activity_score
        return 0.0
    except Exception as e:
        logger.error(f"Error extracting activity level: {str(e)}")
        return 0.0

def extract_sleep_quality(sleep_data: dict) -> float:
    """Extract sleep quality from sleep data"""
    try:
        if 'sleep' in sleep_data and sleep_data['sleep']:
            sleep = sleep_data['sleep'][0]
            # Calculate sleep quality based on efficiency and duration
            efficiency = float(sleep.get('efficiency', 0))
            duration_hours = float(sleep.get('duration', 0)) / (1000 * 60 * 60)  # Convert ms to hours
            
            # Weight both factors
            sleep_quality = (efficiency * 0.6 + 
                           min(duration_hours / 8.0 * 100, 100) * 0.4)  # 8 hours is optimal
            return sleep_quality
        return 0.0
    except Exception as e:
        logger.error(f"Error extracting sleep quality: {str(e)}")
        return 0.0

def calculate_heart_rate_score(heart_rate: float) -> float:
    """Calculate heart rate score (0-100)"""
    try:
        # Define healthy heart rate range (60-100 bpm)
        if 60 <= heart_rate <= 100:
            return 100.0
        elif heart_rate < 60:
            return max(0, 100 - (60 - heart_rate) * 2)
        else:  # heart_rate > 100
            return max(0, 100 - (heart_rate - 100) * 2)
    except Exception as e:
        logger.error(f"Error calculating heart rate score: {str(e)}")
        return 0.0

def calculate_activity_score(activity_level: float) -> float:
    """Calculate activity score (0-100)"""
    try:
        # Define target activity minutes (150 minutes per week = ~22 minutes per day)
        daily_target = 22.0
        
        if activity_level >= daily_target:
            return 100.0
        else:
            return (activity_level / daily_target) * 100
    except Exception as e:
        logger.error(f"Error calculating activity score: {str(e)}")
        return 0.0

def calculate_sleep_score(sleep_quality: float) -> float:
    """Calculate sleep score (0-100)"""
    try:
        # Sleep quality is already on a 0-100 scale
        return min(100.0, max(0.0, sleep_quality))
    except Exception as e:
        logger.error(f"Error calculating sleep score: {str(e)}")
        return 0.0

def calculate_fatigue_score(heart_rate_data, activity_data, sleep_data):
    """Calculate fatigue score based on all available metrics"""
    try:
        # Extract relevant values from data
        current_heart_rate = extract_current_heart_rate(heart_rate_data)
        activity_level = extract_activity_level(activity_data)
        sleep_quality = extract_sleep_quality(sleep_data)

        # Calculate individual scores (0-100)
        heart_rate_score = calculate_heart_rate_score(current_heart_rate)
        activity_score = calculate_activity_score(activity_level)
        sleep_score = calculate_sleep_score(sleep_quality)

        # Weighted average for final score
        weights = {
            'heart_rate': 0.3,
            'activity': 0.3,
            'sleep': 0.4
        }

        final_score = (
            heart_rate_score * weights['heart_rate'] +
            activity_score * weights['activity'] +
            sleep_score * weights['sleep']
        )

        return {
            'score': round(final_score, 1),
            'level': 'Normal' if final_score >= 80 else 'Warning' if final_score >= 60 else 'Danger',
            'factors': {
                'heart_rate': {
                    'value': current_heart_rate,
                    'score': heart_rate_score,
                    'contribution': weights['heart_rate']
                },
                'activity': {
                    'value': activity_level,
                    'score': activity_score,
                    'contribution': weights['activity']
                },
                'sleep': {
                    'value': sleep_quality,
                    'score': sleep_score,
                    'contribution': weights['sleep']
                }
            },
            'timestamp': datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error calculating fatigue score: {str(e)}")
        return {
            'score': 0,
            'level': 'Error',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }

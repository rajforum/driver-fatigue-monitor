from flask import Blueprint, abort, redirect, session, url_for, jsonify
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from datetime import datetime, timedelta

fatigue_bp = Blueprint('fatigue', __name__)

def login_required(func):
    def wrapper(*args, **kwargs):
        if "google_credentials" not in session:
            return redirect(url_for("google_auth.login"))
        else:
            return func(*args, **kwargs)
        
    wrapper.__name__ = "login_required_" + func.__name__
    return wrapper

@fatigue_bp.route('/')
def home():
    return "Driver Fatigue Monitoring Solution <a href='/login'>Login</a>"

@fatigue_bp.route('/dashboard')
@login_required
def dashboard():
    # TODO: Add dashboard logic 
    return "Dashboard"

@fatigue_bp.route('/fitness_data')
@login_required
def get_fitness_data():
    try:
        credentials = Credentials(**session['google_credentials'])
        fitness_service = build('fitness', 'v1', credentials=credentials)

        # Get heart rate data for the last 24 hours
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

        data = fitness_service.users().dataset().aggregate(userId="me", body=body).execute()
        
        return jsonify(data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@fatigue_bp.route('/activity_data')
@login_required
def get_activity_data():
    try:
        credentials = Credentials(**session['google_credentials'])
        fitness_service = build('fitness', 'v1', credentials=credentials)

        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=6)  # Last 6 hours of activity

        body = {
            "aggregateBy": [{
                "dataTypeName": "com.google.step_count.delta"
            }, {
                "dataTypeName": "com.google.activity.segment"
            }],
            "bucketByTime": {"durationMillis": 900000},  # 15-minute buckets
            "startTimeMillis": int(start_time.timestamp() * 1000),
            "endTimeMillis": int(end_time.timestamp() * 1000)
        }

        data = fitness_service.users().dataset().aggregate(userId="me", body=body).execute()
        return jsonify(data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@fatigue_bp.route('/sleep_data')
@login_required
def get_sleep_data():
    try:
        credentials = Credentials(**session['google_credentials'])
        fitness_service = build('fitness', 'v1', credentials=credentials)

        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=1)  # Last 24 hours

        body = {
            "aggregateBy": [{
                "dataTypeName": "com.google.sleep.segment"
            }],
            "bucketByTime": {"durationMillis": 3600000},  # 1-hour buckets
            "startTimeMillis": int(start_time.timestamp() * 1000),
            "endTimeMillis": int(end_time.timestamp() * 1000)
        }

        data = fitness_service.users().dataset().aggregate(userId="me", body=body).execute()
        return jsonify(data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@fatigue_bp.route('/analyze_fatigue')
@login_required
def analyze_fatigue():
    """Analyze fatigue based on combined metrics"""
    try:
        # Here we'll combine heart rate, activity, and sleep data
        # to create a simple fatigue score
        heart_rate = get_fitness_data().get_json()
        activity = get_activity_data().get_json()
        sleep = get_sleep_data().get_json()

        # TODO: Implement fatigue analysis algorithm
        fatigue_score = {
            'score': 0,  # 0-100 scale
            'heart_rate_data': heart_rate,
            'activity_data': activity,
            'sleep_data': sleep,
            'timestamp': datetime.utcnow().isoformat()
        }

        return jsonify(fatigue_score)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

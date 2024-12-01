from flask import Blueprint, jsonify, redirect, session, url_for
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from datetime import datetime, timedelta
from app.services.google_health import get_google_fit_data

fatigue_bp = Blueprint('fatigue', __name__)

def login_required(func):
    def wrapper(*args, **kwargs):
        if "google_credentials" not in session:
            return redirect(url_for("google_auth.login"))
        else:
            return func(*args, **kwargs)
        
    wrapper.__name__ = "login_required_" + func.__name__
    return wrapper

@fatigue_bp.route('/health_data')
@login_required
def health_data():
    credentials = Credentials(**session['google_credentials'])
    data = get_google_fit_data(credentials)
    return jsonify(data)

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

@fatigue_bp.route('/analyze_fatigue')
@login_required
def analyze_fatigue():
    """Analyze fatigue based on combined metrics"""
    try:
        heart_rate = get_fitness_data().get_json()
        activity = 1 # get_activity_data().get_json()
        sleep = 1 # get_sleep_data().get_json()

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

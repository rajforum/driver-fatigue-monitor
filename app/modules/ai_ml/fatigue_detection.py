# app/modules/ai_ml/fatigue_detection.py
"""
Now that we have the fatigue detection model and threshold analyzer, 
we can integrate them into the Flask API. This will involve creating a new route that processes the input data 
(such as eye movement and biometric data), makes predictions, and returns an alert message.
"""

from flask import Blueprint, request, jsonify
from app.modules.ai_ml.fatigue_model import FatigueDetectionModel
from app.modules.ai_ml.threshold_analyzer import ThresholdAnalyzer

ai_ml_bp = Blueprint('ai_ml', __name__)

# Initialize the model and analyzer
fatigue_model = FatigueDetectionModel()
threshold_analyzer = ThresholdAnalyzer()

@ai_ml_bp.route('/detect_fatigue', methods=['POST'])
def detect_fatigue():
    data = request.get_json()
    
    # Extract input features
    eye_blink_rate = data.get('eye_blink_rate', 0)  # Example feature
    head_tilt = data.get('head_tilt', 0)  # Example feature
    heart_rate = data.get('heart_rate', 0)  # Example feature
    
    # Create feature vector
    features = [eye_blink_rate, head_tilt, heart_rate]  # Extend this with more features
    
    # Predict the fatigue score
    fatigue_score = fatigue_model.predict_proba([features])[0]
    
    # Analyze the fatigue score
    alert_message = threshold_analyzer.analyze(fatigue_score)
    
    # Return the result
    return jsonify({
        'fatigue_score': fatigue_score,
        'alert': alert_message
    })

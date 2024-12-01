from app import socketio
from flask_socketio import emit
import time

# Store the latest metrics
latest_metrics = {
    "heartRate": "--",
    "alertness": "--",
    "blinkRate": "--",
    "eyeClosure": "--",
    "headPosition": "--",
    "alertStatus": "Normal"
}

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('request_metrics')
def handle_metrics_request():
    emit('metrics_update', latest_metrics)

def update_metrics(new_metrics):
    """Update the latest metrics and emit to all clients"""
    global latest_metrics
    
    # Convert metrics to frontend format
    latest_metrics = {
        "heartRate": "75",  # This could be from a different sensor
        "alertness": f"{new_metrics['alertness']}",
        "blinkRate": f"{new_metrics['blink_rate']} blinks/min",
        "eyeClosure": f"{new_metrics['eye_closure_duration']:.1f}s",
        "headPosition": new_metrics['head_position'],
        "alertStatus": "Warning" if new_metrics['alertness'] < 70 else "Normal"
    }
    
    # Emit to all connected clients
    socketio.emit('metrics_update', latest_metrics) 
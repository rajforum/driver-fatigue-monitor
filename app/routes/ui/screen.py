from flask import Blueprint, render_template, session, Response
from app.routes.fatigue import login_required
from app.modules.data_collection import generate_frames

ui_screen_bp = Blueprint('ui_screen', __name__)

@ui_screen_bp.route('/')
def home():
    return "Driver Fatigue Monitoring Solution <a href='/google-auth/login'>Login</a>"

@ui_screen_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@ui_screen_bp.route('/live')
@login_required
def live_monitor():
    return render_template('live_monitor.html')

@ui_screen_bp.route('/video_feed')
@login_required
def video_feed():
    """Video streaming route."""
    return Response(
        generate_frames(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    ) 
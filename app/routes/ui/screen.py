from flask import Blueprint, render_template, session, Response, redirect, url_for
from app.routes.fatigue import login_required
from app.modules.data_collection import generate_frames

ui_screen_bp = Blueprint('ui_screen', __name__)

@ui_screen_bp.route('/')
def home():
    """Home page route"""
    return render_template('home.html', active_page='home')

@ui_screen_bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard route that requires login"""
    return render_template('dashboard.html', active_page='dashboard')

@ui_screen_bp.route('/live')
@login_required
def live():
    """Live feed with metrics route that requires login"""
    return render_template('live_monitor.html', active_page='live')

@ui_screen_bp.route('/video_feed')
@login_required
def video_feed():
    """Video streaming route."""
    return Response(
        generate_frames(session.get('user_info', {})),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    ) 
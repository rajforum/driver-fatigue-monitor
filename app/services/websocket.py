import json
from flask import request, session, current_app
from flask.ctx import RequestContext
from flask_socketio import SocketIO, emit
from datetime import datetime
import logging

from app.config import Config
from app.services.metrics import get_real_metrics
from app.services.mock_data import get_mock_metrics
from app.modules.data_collection import get_current_performance

logger = logging.getLogger(__name__)

class SocketService:
    def __init__(self):
        self.socketio = SocketIO()
        self.initialized = False
        self.active_connections = set()
        self.trend_service = None
        self.app = None

    def init_app(self, app):
        if self.initialized:
            return
        
        self.app = app
        from app.services.trends import TrendService
        self.trend_service = TrendService()
        
        self.socketio.init_app(app, cors_allowed_origins="*")
        self.setup_handlers()
        self.initialized = True

    def setup_handlers(self):
        @self.socketio.on('connect')
        def handle_connect():
            logger.info('Client connected')
            self.active_connections.add(request.sid)
            
        @self.socketio.on('disconnect')
        def handle_disconnect():
            logger.info('Client disconnected')
            self.active_connections.discard(request.sid)
            
        @self.socketio.on('ping')
        def handle_ping():
            """Handle heartbeat ping from client"""
            self.socketio.emit('pong')
            
        @self.socketio.on('request_metrics')
        def handle_metrics_request():
            from app.services.service_manager import ServiceManager
            try:
                metrics = ServiceManager.get_instance().metrics.get_metrics()
                if 'error' in metrics:
                    logger.error(f"Error getting metrics: {metrics['error']}")
                    self.socketio.emit('metrics_error', {'message': metrics['error']})
                else:
                    self.socketio.emit('metrics_update', metrics)
            except Exception as e:
                logger.error(f"Error in metrics request: {str(e)}")
                self.socketio.emit('metrics_error', {'message': 'Internal server error'})

        @self.socketio.on('request_trends')
        def handle_trends_request():
            try:
                user_email = session.get('user_info', {}).get('email')
                if not user_email:
                    emit('trends_error', {'message': 'User not authenticated'})
                    return

                trend_data = self.trend_service.get_trend_data(user_email)
                emit('trends_update', trend_data)
            except Exception as e:
                logger.error(f"Error in trends request: {str(e)}")
                emit('trends_error', {'message': 'Error fetching trends'})

    def cleanup(self):
        """Clean up socket connections and resources"""
        try:
            self.disconnect_all_clients()
            self.socketio = None
            self.initialized = False
        except Exception as e:
            logger.error(f"Error cleaning up socket service: {str(e)}")

    def shutdown(self):
        """Graceful shutdown of socket service"""
        try:
            # Notify all clients of shutdown
            self.socketio.emit('server_shutdown', {'message': 'Server is shutting down'})
            self.cleanup()
        except Exception as e:
            logger.error(f"Error shutting down socket service: {str(e)}")

    def disconnect_all_clients(self):
        """Disconnect all connected clients"""
        try:
            for sid in self.active_connections:
                self.socketio.disconnect(sid)
            self.active_connections.clear()
        except Exception as e:
            logger.error(f"Error disconnecting clients: {str(e)}")

    def get_metrics(self):
        """Get metrics and save for trends"""
        try:
            metrics = get_mock_metrics() if Config.USE_MOCK_DATA else get_real_metrics()
            
            # Save metrics for trends
            user_email = session.get('user_info', {}).get('email')
            if user_email:
                self.trend_service.save_metrics_snapshot(user_email, metrics)
            
            # Get real performance metrics from data collection
            performance_metrics = get_current_performance()
            
            # Add eye state, detection status, and real performance metrics
            metrics.update({
                'isDetecting': True,  # This should come from your face detection
                'eyeState': 'open',   # This should come from your eye detection
                'fps': performance_metrics['fps'],
                'processingTime': performance_metrics['processingTime'],
                'frameCount': performance_metrics['frameCount'],
                'avgFrameInterval': performance_metrics['avgFrameInterval']
            })
            
            return metrics
        except Exception as e:
            logger.error(f"Error getting metrics: {str(e)}")
            return {
                'error': str(e),
                'isDetecting': False,
                'eyeState': None,
                'fps': 0,
                'processingTime': 0
            } 
        
    def update_metrics(self,new_metrics):
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
        self.socketio.emit('metrics_update', latest_metrics) 

    def emit_metrics(self, metrics):
        """Emit metrics to all connected clients"""
        try:
            # Convert metrics to frontend format
            formatted_metrics = {
                "heartRate": "75",  # This could be from a different sensor
                "alertness": f"{metrics.get('alertness', 0)}",
                "blinkRate": f"{metrics.get('blink_rate', 0)} blinks/min",
                "yawnCount": f"{metrics.get('yawn_count', 0)} yawns/min",
                "eyeClosure": f"{metrics.get('eye_closure_duration', 0):.1f}s",
                "headPosition": metrics.get('head_position', 'Unknown'),
                "alertStatus": "Warning" if metrics.get('alertness', 100) < 70 else "Normal",
                "isDetecting": metrics.get('isDetecting', False),  # Add detection status
                "eyeState": metrics.get('eyeState', 'open')  # Add eye state
            }

            # Create minimal request environment if needed
            if not current_app:
                environ = {
                    'wsgi.version': (1, 0),
                    'wsgi.url_scheme': 'http',
                    'REQUEST_METHOD': 'GET',
                    'PATH_INFO': '/',
                    'SERVER_NAME': 'localhost',
                    'SERVER_PORT': '5000',
                    'wsgi.input': None,
                    'wsgi.errors': None,
                    'wsgi.multithread': False,
                    'wsgi.multiprocess': False,
                    'wsgi.run_once': False
                }
                ctx = self.app.request_context(environ)
                ctx.push()
                try:
                    # Save metrics for trends if user is logged in
                    if hasattr(session, 'get'):
                        user_email = session.get('user_info', {}).get('email')
                        if user_email and self.trend_service:
                            self.trend_service.save_metrics_snapshot(user_email, formatted_metrics)
                    
                    # Emit to all connected clients
                    self.socketio.emit('metrics_update', formatted_metrics)
                finally:
                    ctx.pop()
            else:
                # We're already in a request context
                if hasattr(session, 'get'):
                    user_email = session.get('user_info', {}).get('email')
                    if user_email and self.trend_service:
                        self.trend_service.save_metrics_snapshot(user_email, formatted_metrics)
                
                # Emit to all connected clients
                self.socketio.emit('metrics_update', formatted_metrics)

        except Exception as e:
            logger.error(f"Error emitting metrics: {str(e)}")
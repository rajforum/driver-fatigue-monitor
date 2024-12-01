import json
from flask_socketio import SocketIO, emit
from datetime import datetime
from app.services.metrics import get_metrics
import logging

logger = logging.getLogger(__name__)
socketio = SocketIO()

def init_websocket(app):
    socketio.init_app(app, cors_allowed_origins="*")
    
    @socketio.on('connect')
    def handle_connect():
        logger.info('Client connected')
        
    @socketio.on('disconnect')
    def handle_disconnect():
        logger.info('Client disconnected')
        
    @socketio.on('request_metrics')
    def handle_metrics_request():
        try:
            metrics = get_metrics()
            if 'error' in metrics:
                logger.error(f"Error getting metrics: {metrics['error']}")
                emit('metrics_error', {'message': metrics['error']})
            else:
                emit('metrics_update', metrics)
        except Exception as e:
            logger.error(f"Error in metrics request: {str(e)}")
            emit('metrics_error', {'message': 'Internal server error'}) 
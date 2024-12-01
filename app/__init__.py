import os
import logging
from flask import Flask
from dotenv import load_dotenv
from app.core.logging_config import setup_logging
from app.routes.google_auth import google_auth_bp
from app.routes.fatigue import fatigue_bp
from app.routes.ui.screen import ui_screen_bp
from app.utils.firebase_client import FirebaseClient
from app.services.websocket import init_websocket, socketio


os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1' # For development only to allow HTTP

# Load environment variables
load_dotenv()  

# Create, configure, register blueprints and return the Flask app
def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv("SECRET_KEY")

    setup_logging()

    # Example logging statements
    logger = logging.getLogger(__name__)
    logger.info("App Starting ::: Fatigue Monitoring Solution is starting...")
    
    # Initialize Firebase client
    FirebaseClient().initialize()

    # Register blueprints
    app.register_blueprint(google_auth_bp)
    app.register_blueprint(fatigue_bp)
    app.register_blueprint(ui_screen_bp)

    # Initialize Socket.IO with the app
    init_websocket(app)

    return app
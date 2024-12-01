import os
import logging
from flask import Flask
from dotenv import load_dotenv
from app.core.logging_config import setup_logging
from app.routes.google_auth import google_auth_bp
from app.routes.fatigue import fatigue_bp
from app.routes.ui.screen import ui_screen_bp
from app.routes.fitbit_auth import fitbit_auth_bp
from app.utils.firebase_client import FirebaseClient
from app.services.service_manager import ServiceManager
from app.core.error_handlers import register_error_handlers


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
    
    # Initialize Firebase client first
    FirebaseClient().initialize()

    # Initialize all services
    service_manager = ServiceManager.get_instance()
    service_manager.initialize(app)

    # Register blueprints with prefixes
    app.register_blueprint(google_auth_bp, url_prefix='/google-auth')
    app.register_blueprint(fitbit_auth_bp, url_prefix='/fitbit-auth')
    app.register_blueprint(fatigue_bp, url_prefix='/api/fatigue')
    app.register_blueprint(ui_screen_bp, url_prefix='/ui')

    # Register error handlers
    register_error_handlers(app)

    # # Register cleanup handlers
    # @app.teardown_appcontext
    # def cleanup_services(exception=None):
    #     """Clean up services when the app context tears down"""
    #     try:
    #         service_manager.cleanup()
    #     except Exception as e:
    #         logger.error(f"Error during service cleanup: {str(e)}")

    # # Handle graceful shutdown
    # import atexit
    # atexit.register(service_manager.shutdown)

    return app


    # app.register_blueprint(google_auth_bp, url_prefix='/google-auth')
    # app.register_blueprint(fitbit_auth_bp, url_prefix='/fitbit-auth')
    # app.register_blueprint(fatigue_bp, url_prefix='/api/fatigue')
    # app.register_blueprint(ui_screen_bp, url_prefix='/ui')
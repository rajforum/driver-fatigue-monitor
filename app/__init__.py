from flask import Flask
from .utils.firebase_client import init_firebase

# from .routes import fatigue

def create_app():
    app = Flask(__name__)
    # app.config.from_mapping(
    #     SECRET_KEY='dev',  # Change this in production
    # )

    # Register blueprints
    # app.register_blueprint(fatigue.bp)

     # Initialize Firebase client
    db = init_firebase()
    
    # Additional app setup, like routes or blueprints
    @app.route('/')
    def home():
        return "Driver Fatigue Monitoring Solution"
    

    return app

import os

class Config:
    # Other configs...
    USE_MOCK_DATA = True  # Switch to False to use real data 
    MOCK_DATA_SOURCE = 'fitbit'  # or 'simple' for basic mock data
    
    # Environment variables
    ENVIRONMENT = os.getenv("ENVIRONMENT")
    IS_DEVELOPMENT = ENVIRONMENT == "development"
    HOST = os.getenv("HOST")
    PORT = os.getenv("PORT")
    HOST_URL = os.getenv("HOST_URL")

    # Google OAuth API Configuration
    GOOGLE_OAUTH_REDIRECT_URI = f'{HOST_URL}/google-auth/oauth2callback'

    # Fitbit API Configuration
    FITBIT_CLIENT_ID = 'your_client_id'
    FITBIT_CLIENT_SECRET = 'your_client_secret'
    FITBIT_REDIRECT_URI = f'{HOST_URL}/fitbit-auth/callback'
    
    # Fitbit API Scopes
    FITBIT_SCOPES = [
        'activity',
        'heartrate',
        'location',
        'nutrition',
        'profile',
        'settings',
        'sleep',
        'social',
        'weight'
    ]
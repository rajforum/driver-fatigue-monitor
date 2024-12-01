import os
from app.utils.firebase_client import FirebaseClient
from definition import CONFIG_DIR
from app.config import Config
from flask import Blueprint, Request, redirect, url_for, session, request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow

google_auth_bp = Blueprint('google_auth', __name__)

# Reference: https://developers.google.com/fit/overview
SCOPES = [
    # User Info
    'https://www.googleapis.com/auth/userinfo.email', 
    'https://www.googleapis.com/auth/userinfo.profile',
    'openid',

    # Google Fit - Activity
    'https://www.googleapis.com/auth/fitness.activity.read',  

    # Google Fit - Location
    'https://www.googleapis.com/auth/fitness.location.read',

    # Google Fit - Nutrition
    'https://www.googleapis.com/auth/fitness.nutrition.read',

    # Google Fit - Health
    'https://www.googleapis.com/auth/fitness.blood_glucose.read',
    'https://www.googleapis.com/auth/fitness.blood_pressure.read',
    'https://www.googleapis.com/auth/fitness.body.read',
    'https://www.googleapis.com/auth/fitness.body_temperature.read',
    'https://www.googleapis.com/auth/fitness.reproductive_health.read',
    'https://www.googleapis.com/auth/fitness.heart_rate.read',
    'https://www.googleapis.com/auth/fitness.oxygen_saturation.read',
    'https://www.googleapis.com/auth/fitness.sleep.read'
]

CLIENT_SECRET_PATH = os.path.join(CONFIG_DIR, "client-secret.json")
flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_PATH, scopes=SCOPES, redirect_uri=Config.GOOGLE_OAUTH_REDIRECT_URI)


# Route to initiate the login
@google_auth_bp.route('/login')
def login():
    authorization_url, state = flow.authorization_url(prompt='consent')
    session['state'] = state
    return redirect(authorization_url)

# Route to logout
@google_auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('ui_screen.home'))

# login oauth callback route
@google_auth_bp.route('/oauth2callback')
def oauth2callback():
    flow.fetch_token(authorization_response=request.url)

    if session.get('state') != request.args.get('state'):
        return 'Error: State mismatch!', 500


    credentials = flow.credentials
    user_info = fetch_user_info(credentials)

    session['google_credentials'] = credentials_to_dict(credentials)
    session['user_info'] = user_info

    # Store credentials in Firestore under user email
    store_user_info(user_info, credentials)

    return redirect(url_for('ui_screen.dashboard'))

@google_auth_bp.route("/home")
def home():
    return "Home Page: Google Fit data can be accessed here."

# Route to display user profile
@google_auth_bp.route('/profile')
def profile():
    if 'google_credentials' not in session:
        return redirect(url_for('google_auth.login'))

    credentials = Credentials(**session['google_credentials'])
    
    # Check if token is expired, if so, refresh it
    credentials = refresh_access_token(credentials)

    if credentials:
        session['google_credentials'] = credentials_to_dict(credentials)

    # Access user info using the credentials
    # Access user info using the credentials
    user_info = fetch_user_info(credentials)

    return f"Welcome, {user_info.get('name')}! Your email is {user_info.get('email')}."

# Utility function to save credentials as a dictionary
def credentials_to_dict(credentials):
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }


def refresh_access_token(credentials):
    if credentials and credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
        return credentials
    return credentials

def fetch_user_info(credentials):
    # Use credentials to get user info from Google API
    oauth2_service = build('oauth2', 'v2', credentials=credentials)
    user_info = oauth2_service.userinfo().get().execute()
    
    # Return the user info (you can customize which data you need)
    return user_info

def store_user_info(user_info, credentials):
    user_ref = FirebaseClient().get_db().collection('users').document(user_info['email'])
    user_ref.set({
        'name': user_info.get('name'),
        'email': user_info.get('email'),
        'access_token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_expiry': credentials.expiry
    })
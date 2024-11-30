import os
from definition import CLIENT_SECRET_PATH, AUTH2_REDIRECT_URI, CONFIG_DIR
from flask import Blueprint, redirect, url_for, session, request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2 import id_token

google_auth_bp = Blueprint('google_auth', __name__)

SCOPES = [
    'https://www.googleapis.com/auth/userinfo.email', 
    'https://www.googleapis.com/auth/userinfo.profile',
    'openid',

    # 'https://www.googleapis.com/auth/fitness.activity.read',
    # 'https://www.googleapis.com/auth/fitness.location.read'
]
CLIENT_SECRET_PATH = os.path.join(CONFIG_DIR, "client-secret.json")
flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_PATH, scopes=SCOPES, redirect_uri=AUTH2_REDIRECT_URI)

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
    return redirect(url_for('google_auth.login'))

# login oauth callback route
@google_auth_bp.route('/oauth2callback')
def oauth2callback():
    flow.fetch_token(authorization_response=request.url)

    if session.get('state') != request.args.get('state'):
        return 'Error: State mismatch!', 500


    credentials = flow.credentials
    session['google_credentials'] = credentials_to_dict(credentials)

    return redirect(url_for('google_auth.profile'))

@google_auth_bp.route("/home")
def home():
    return "Home Page: Google Fit data can be accessed here."

# Route to display user profile
@google_auth_bp.route('/profile')
def profile():
    if 'google_credentials' not in session:
        return redirect(url_for('google_auth.login'))

    credentials = Credentials(**session['google_credentials'])

    # Access user info using the credentials
    from googleapiclient.discovery import build
    oauth2_service = build('oauth2', 'v2', credentials=credentials)
    user_info = oauth2_service.userinfo().get().execute()

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

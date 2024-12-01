from flask import Blueprint, redirect, url_for, session, request
import requests
from app.config import Config
from app.utils.firebase_client import FirebaseClient
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

fitbit_auth_bp = Blueprint('fitbit_auth', __name__)

@fitbit_auth_bp.route('/login')
def login():
    """Initiate Fitbit OAuth flow"""
    auth_url = (
        'https://www.fitbit.com/oauth2/authorize?'
        f'client_id={Config.FITBIT_CLIENT_ID}'
        f'&redirect_uri={Config.FITBIT_REDIRECT_URI}'
        '&response_type=code'
        f'&scope={" ".join(Config.FITBIT_SCOPES)}'
    )
    return redirect(auth_url)

@fitbit_auth_bp.route('/callback')
def callback():
    """Handle Fitbit OAuth callback"""
    try:
        code = request.args.get('code')
        if not code:
            return 'Authorization code not received.', 400

        # Exchange code for token
        token_response = requests.post(
            'https://api.fitbit.com/oauth2/token',
            data={
                'client_id': Config.FITBIT_CLIENT_ID,
                'client_secret': Config.FITBIT_CLIENT_SECRET,
                'code': code,
                'grant_type': 'authorization_code',
                'redirect_uri': Config.FITBIT_REDIRECT_URI
            },
            headers={
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        )
        token_data = token_response.json()

        if 'access_token' not in token_data:
            return 'Failed to get access token.', 400

        # Store tokens and expiration in session
        session['fitbit_token'] = token_data['access_token']
        session['fitbit_refresh_token'] = token_data.get('refresh_token')
        
        # Calculate and store token expiration time
        expires_in = token_data.get('expires_in', 3600)  # Default to 1 hour if not provided
        expiry_time = datetime.utcnow() + timedelta(seconds=expires_in)
        session['fitbit_token_expiry'] = expiry_time.isoformat()

        # Get user info
        user_response = requests.get(
            'https://api.fitbit.com/1/user/-/profile.json',
            headers={
                'Authorization': f'Bearer {token_data["access_token"]}'
            }
        )
        user_data = user_response.json()['user']

        # Store in Firebase if user is logged in with Google
        if 'user_info' in session:
            user_email = session['user_info'].get('email')
            if user_email:
                FirebaseClient().get_db().collection('users').document(user_email).update({
                    'fitbit_connected': True,
                    'fitbit_token': token_data['access_token'],
                    'fitbit_refresh_token': token_data.get('refresh_token'),
                    'fitbit_user_id': user_data.get('encodedId'),
                    'fitbit_connected_at': datetime.utcnow()
                })

        return redirect(url_for('ui_screen.dashboard'))

    except Exception as e:
        logger.error(f"Error in Fitbit callback: {str(e)}")
        return f'Error during authentication: {str(e)}', 500

@fitbit_auth_bp.route('/refresh')
def refresh_token():
    """Refresh Fitbit access token"""
    try:
        if 'fitbit_refresh_token' not in session:
            return {'error': 'No refresh token available'}, 401

        response = requests.post(
            'https://api.fitbit.com/oauth2/token',
            data={
                'grant_type': 'refresh_token',
                'refresh_token': session['fitbit_refresh_token'],
                'client_id': Config.FITBIT_CLIENT_ID,
                'client_secret': Config.FITBIT_CLIENT_SECRET
            },
            headers={
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        )

        token_data = response.json()
        if 'access_token' in token_data:
            session['fitbit_token'] = token_data['access_token']
            session['fitbit_refresh_token'] = token_data.get('refresh_token')
            
            # Update expiration time
            expires_in = token_data.get('expires_in', 3600)
            expiry_time = datetime.utcnow() + timedelta(seconds=expires_in)
            session['fitbit_token_expiry'] = expiry_time.isoformat()
            
            # Update Firebase if user is logged in
            if 'user_info' in session:
                user_email = session['user_info'].get('email')
                if user_email:
                    FirebaseClient().get_db().collection('users').document(user_email).update({
                        'fitbit_token': token_data['access_token'],
                        'fitbit_refresh_token': token_data.get('refresh_token'),
                        'fitbit_token_expiry': expiry_time
                    })
            
            return {'success': True}
        
        return {'error': 'Failed to refresh token'}, 401

    except Exception as e:
        logger.error(f"Error refreshing Fitbit token: {str(e)}")
        return {'error': str(e)}, 500

@fitbit_auth_bp.route('/disconnect')
def disconnect():
    """Disconnect Fitbit account"""
    try:
        if 'fitbit_token' in session:
            # Revoke token at Fitbit
            requests.post(
                'https://api.fitbit.com/oauth2/revoke',
                data={'token': session['fitbit_token']},
                headers={
                    'Authorization': f'Basic {Config.FITBIT_CLIENT_ID}:{Config.FITBIT_CLIENT_SECRET}'
                }
            )

            # Remove from session
            session.pop('fitbit_token', None)
            session.pop('fitbit_refresh_token', None)

            # Update Firebase if user is logged in
            if 'user_info' in session:
                user_email = session['user_info'].get('email')
                if user_email:
                    FirebaseClient().get_db().collection('users').document(user_email).update({
                        'fitbit_connected': False,
                        'fitbit_token': None,
                        'fitbit_refresh_token': None,
                        'fitbit_disconnected_at': datetime.utcnow()
                    })

        return redirect(url_for('ui_screen.dashboard'))

    except Exception as e:
        logger.error(f"Error disconnecting Fitbit: {str(e)}")
        return f'Error disconnecting Fitbit: {str(e)}', 500 
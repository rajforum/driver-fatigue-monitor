from functools import wraps
from flask import session, redirect, url_for
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

def check_fitbit_token(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            # Check if token exists
            if 'fitbit_token' not in session:
                logger.warning("No Fitbit token found in session")
                return redirect(url_for('fitbit_auth.login'))

            # Check if token expiration time exists
            if 'fitbit_token_expiry' not in session:
                logger.warning("No token expiry time found")
                return redirect(url_for('fitbit_auth.login'))

            # Check if token is expired or about to expire (within 5 minutes)
            expiry = datetime.fromisoformat(session['fitbit_token_expiry'])
            if expiry <= datetime.utcnow() + timedelta(minutes=5):
                logger.info("Token expired or about to expire, refreshing...")
                # Try to refresh the token
                refresh_response = redirect(url_for('fitbit_auth.refresh_token'))
                if refresh_response.status_code != 200:
                    logger.error("Failed to refresh token")
                    return redirect(url_for('fitbit_auth.login'))

            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in check_fitbit_token: {str(e)}")
            return redirect(url_for('fitbit_auth.login'))

    return wrapper 
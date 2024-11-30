from flask import Blueprint, session, redirect, request, jsonify
from app.modules.wearable.fitbit_api import generate_auth_url, fetch_access_token, get_fitbit_data
from app.modules.wearable import initiate_auth_flow, exchange_code, fetch_data_with_fallback

wearable_bp = Blueprint("wearable", __name__)

@wearable_bp.route("/wearable/authorize", methods=["GET"])
def authorize():
    """Redirect to Fitbit authorization page."""
    return redirect(generate_auth_url())

@wearable_bp.route("/wearable/callback", methods=["GET"])
def callback():
    """Handle Fitbit OAuth callback."""
    auth_code = request.args.get("code")
    if not auth_code:
        return jsonify({"error": "Authorization code missing"}), 400

    token_data = fetch_access_token(auth_code)
    if not token_data:
        return jsonify({"error": "Failed to fetch access token"}), 500

    # Save token data in session or database for later use
    session["fitbit_access_token"] = token_data["access_token"]
    session["refresh_token"] = token_data["refresh_token"]
    session["expires_in"] = token_data["expires_in"]

    return jsonify({"message": "Fitbit authorization successful", "data": token_data})

## Authentication APIs
@wearable_bp.route("/wearable/fetch_data", methods=["GET"])
def fetch_data():
    """Fetch user data from Fitbit API."""
    access_token = session.get("fitbit_access_token")
    if not access_token:
        return jsonify({"error": "Access token not found"}), 401

    data = get_fitbit_data(access_token, "activities/heart")
    if not data:
        return jsonify({"error": "Failed to fetch Fitbit data"}), 500

    return jsonify({"message": "Fitbit data fetched successfully", "data": data})

@wearable_bp.route('/wearable/auth', methods=['GET'])
def wearable_auth():
    auth_url = initiate_auth_flow()
    return jsonify({"auth_url": auth_url})

@wearable_bp.route('/wearable/callback', methods=['GET'])
def wearable_callback():
    code = request.args.get('code')
    if not code:
        return jsonify({"error": "Missing authorization code"}), 400

    tokens = exchange_code(code)
    return jsonify({"message": "Authentication successful", "tokens": tokens})

@wearable_bp.route('/wearable/data', methods=['GET'])
def wearable_data():
    data = fetch_data_with_fallback()
    return jsonify({"data": data})
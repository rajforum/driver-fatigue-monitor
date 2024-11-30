import requests
import os;

# Fitbit API endpoints
AUTH_URL = "https://www.fitbit.com/oauth2/authorize"
TOKEN_URL = "https://api.fitbit.com/oauth2/token"
API_BASE_URL = "https://api.fitbit.com/1/user/-"

# Replace with your actual credentials
CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

def generate_auth_url():
    """Generate the URL for user authorization."""
    return (
        f"{AUTH_URL}?"
        f"response_type=code&client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}&scope=activity heartrate sleep"
    )

def fetch_access_token(auth_code):
    """Exchange the authorization code for an access token."""
    try:
        response = requests.post(
            TOKEN_URL,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "grant_type": "authorization_code",
                "redirect_uri": REDIRECT_URI,
                "code": auth_code,
            },
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching access token: {e}")
        return None

def get_fitbit_data(access_token, endpoint):
    """Fetch data from Fitbit API."""
    try:
        response = requests.get(
            f"{API_BASE_URL}/{endpoint}.json",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching Fitbit data: {e}")
        return None

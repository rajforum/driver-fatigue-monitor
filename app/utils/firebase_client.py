import os
import firebase_admin
from firebase_admin import credentials, firestore
from definition import CONFIG_DIR

def init_firebase():
    # Path to your Firebase service account credentials
    cred = credentials.Certificate(os.path.join(CONFIG_DIR, "driver-fatigue-monitor-firebase-adminsdk.json"))
    
    # Initialize the Firebase app
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
    
    # Get Firestore database
    db = firestore.client()
    return db

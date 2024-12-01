import os
import firebase_admin
from firebase_admin import credentials, firestore
from definition import CONFIG_DIR
import logging

logger = logging.getLogger(__name__)

class FirebaseClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FirebaseClient, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def initialize(self):
        """Initialize Firebase only once."""
        if not self._initialized:
            try:
                self.cred = credentials.Certificate(os.path.join(CONFIG_DIR, "driver-fatigue-monitor-firebase-adminsdk.json"))
                firebase_admin.initialize_app(self.cred)
                self.db = firestore.client()
                self._initialized = True
                logger.info("INITIALIZED ::: Firebase successfully.")
            except Exception as e:
                logger.error(f"Error initializing Firebase: {e}")

    def get_db(self):
        """Get the Firestore client."""
        if not hasattr(self, 'db'):
            raise ValueError("Firebase not initialized. Please call initialize() first.")
        return self.db

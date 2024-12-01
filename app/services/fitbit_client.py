import requests
from datetime import datetime, timedelta
import logging
from typing import Dict, Optional
from app.utils.auth_decorators import check_fitbit_token

logger = logging.getLogger(__name__)

class FitbitClient:
    BASE_URL = "https://api.fitbit.com/1/user/-"
    
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json'
        }

    @check_fitbit_token
    def get_heart_rate_data(self, date: Optional[str] = None) -> Dict:
        """Get heart rate data for a specific date"""
        try:
            if not date:
                date = datetime.now().strftime('%Y-%m-%d')
            
            url = f"{self.BASE_URL}/activities/heart/date/{date}/1d/1sec.json"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting heart rate data: {str(e)}")
            return {}

    @check_fitbit_token
    def get_sleep_data(self, date: Optional[str] = None) -> Dict:
        """Get sleep data for a specific date"""
        try:
            if not date:
                date = datetime.now().strftime('%Y-%m-%d')
            
            url = f"{self.BASE_URL}/sleep/date/{date}.json"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting sleep data: {str(e)}")
            return {}

    @check_fitbit_token
    def get_activity_data(self, date: Optional[str] = None) -> Dict:
        """Get activity data for a specific date"""
        try:
            if not date:
                date = datetime.now().strftime('%Y-%m-%d')
            
            url = f"{self.BASE_URL}/activities/date/{date}.json"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting activity data: {str(e)}")
            return {}

    @check_fitbit_token
    def get_all_metrics(self) -> Dict:
        """Get all relevant metrics for fatigue monitoring"""
        try:
            date = datetime.now().strftime('%Y-%m-%d')
            
            heart_data = self.get_heart_rate_data(date)
            sleep_data = self.get_sleep_data(date)
            activity_data = self.get_activity_data(date)

            # Extract current heart rate
            current_heart_rate = '0'
            if heart_data and 'activities-heart-intraday' in heart_data:
                dataset = heart_data['activities-heart-intraday'].get('dataset', [])
                if dataset:
                    current_heart_rate = str(dataset[-1].get('value', 0))

            # Calculate alertness based on sleep efficiency and activity
            alertness = 100
            if sleep_data and 'sleep' in sleep_data and sleep_data['sleep']:
                sleep_efficiency = sleep_data['sleep'][0].get('efficiency', 90)
                alertness = min(100, sleep_efficiency)

            # Adjust alertness based on activity level
            if activity_data and 'summary' in activity_data:
                sedentary_minutes = activity_data['summary'].get('sedentaryMinutes', 0)
                if sedentary_minutes > 120:  # If sedentary for more than 2 hours
                    alertness = max(0, alertness - 10)

            return {
                'heartRate': current_heart_rate,
                'alertness': str(alertness),
                'blinkRate': '15/min',  # This should come from video processing
                'eyeClosure': '0.2s',    # This should come from video processing
                'headPosition': 'Centered', # This should come from video processing
                'alertStatus': 'Normal' if alertness > 70 else 'Warning',
                'timestamp': datetime.utcnow().isoformat(),
                'raw_data': {
                    'heart_rate': heart_data,
                    'sleep': sleep_data,
                    'activity': activity_data
                }
            }
        except Exception as e:
            logger.error(f"Error getting all metrics: {str(e)}")
            return {
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            } 
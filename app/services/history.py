from datetime import datetime, timedelta
from typing import List, Dict
import json
import logging
from app.utils.firebase_client import FirebaseClient

logger = logging.getLogger(__name__)

class MetricsHistory:
    def __init__(self):
        self.db = FirebaseClient().get_db()

    def save_metrics(self, user_email: str, metrics: Dict):
        """Save metrics to Firebase"""
        try:
            metrics_ref = self.db.collection('metrics').document(user_email)
            metrics_ref.collection('history').add({
                **metrics,
                'timestamp': datetime.utcnow()
            })
        except Exception as e:
            logger.error(f"Error saving metrics: {str(e)}")

    def get_metrics_history(self, user_email: str, hours: int = 24) -> List[Dict]:
        """Get metrics history for the specified duration"""
        try:
            start_time = datetime.utcnow() - timedelta(hours=hours)
            metrics_ref = self.db.collection('metrics').document(user_email)
            
            # Query metrics after start_time
            docs = metrics_ref.collection('history')\
                .where('timestamp', '>=', start_time)\
                .order_by('timestamp', direction='desc')\
                .stream()

            return [doc.to_dict() for doc in docs]
        except Exception as e:
            logger.error(f"Error getting metrics history: {str(e)}")
            return []

    def get_average_metrics(self, user_email: str, hours: int = 1) -> Dict:
        """Calculate average metrics for the specified duration"""
        metrics = self.get_metrics_history(user_email, hours)
        if not metrics:
            return {}

        total_hr = 0
        total_alertness = 0
        count = 0

        for metric in metrics:
            try:
                total_hr += int(metric.get('heartRate', 0))
                total_alertness += float(metric.get('alertness', 0))
                count += 1
            except (ValueError, TypeError):
                continue

        if count == 0:
            return {}

        return {
            'avg_heart_rate': str(total_hr // count),
            'avg_alertness': str(round(total_alertness / count, 2))
        } 
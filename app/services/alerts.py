from datetime import datetime
import logging
from typing import Dict
from app.utils.firebase_client import FirebaseClient
from flask_socketio import emit

logger = logging.getLogger(__name__)

class AlertLevel:
    NORMAL = "normal"
    WARNING = "warning"
    DANGER = "danger"

class AlertService:
    def __init__(self):
        self.db = FirebaseClient().get_db()
        self.thresholds = {
            'blink_rate': {'min': 10, 'max': 30},
            'eye_closure': {'max': 0.3},
            'alertness': {'min': 60},
            'heart_rate': {'min': 50, 'max': 120}
        }

    def check_metrics(self, metrics: Dict, user_email: str):
        """Check metrics against thresholds and emit alerts if needed"""
        try:
            alert_level = self._determine_alert_level(metrics)
            alert_message = self._generate_alert_message(metrics, alert_level)

            if alert_level != AlertLevel.NORMAL:
                self._save_alert(user_email, alert_level, alert_message, metrics)
                self._emit_alert(alert_level, alert_message)

            return alert_level, alert_message

        except Exception as e:
            logger.error(f"Error checking metrics: {str(e)}")
            return AlertLevel.NORMAL, "Error checking metrics"

    def _determine_alert_level(self, metrics: Dict) -> str:
        """Determine alert level based on metrics"""
        try:
            # Check alertness
            alertness = float(metrics.get('alertness', 100))
            if alertness < self.thresholds['alertness']['min']:
                return AlertLevel.DANGER

            # Check blink rate
            blink_rate = float(metrics.get('blinkRate', '15').split('/')[0])
            if (blink_rate < self.thresholds['blink_rate']['min'] or 
                blink_rate > self.thresholds['blink_rate']['max']):
                return AlertLevel.WARNING

            # Check eye closure
            eye_closure = float(metrics.get('eyeClosure', '0.2').replace('s', ''))
            if eye_closure > self.thresholds['eye_closure']['max']:
                return AlertLevel.DANGER

            # Check heart rate
            heart_rate = int(metrics.get('heartRate', 70))
            if (heart_rate < self.thresholds['heart_rate']['min'] or 
                heart_rate > self.thresholds['heart_rate']['max']):
                return AlertLevel.WARNING

            return AlertLevel.NORMAL

        except Exception as e:
            logger.error(f"Error determining alert level: {str(e)}")
            return AlertLevel.NORMAL

    def _generate_alert_message(self, metrics: Dict, alert_level: str) -> str:
        """Generate alert message based on metrics and alert level"""
        if alert_level == AlertLevel.NORMAL:
            return "All metrics normal"

        messages = []
        try:
            # Check alertness
            alertness = float(metrics.get('alertness', 100))
            if alertness < self.thresholds['alertness']['min']:
                messages.append(f"Low alertness level: {alertness}%")

            # Check blink rate
            blink_rate = float(metrics.get('blinkRate', '15').split('/')[0])
            if blink_rate < self.thresholds['blink_rate']['min']:
                messages.append("Blink rate too low")
            elif blink_rate > self.thresholds['blink_rate']['max']:
                messages.append("Blink rate too high")

            # Check eye closure
            eye_closure = float(metrics.get('eyeClosure', '0.2').replace('s', ''))
            if eye_closure > self.thresholds['eye_closure']['max']:
                messages.append("Eyes closed too long")

            # Check heart rate
            heart_rate = int(metrics.get('heartRate', 70))
            if heart_rate < self.thresholds['heart_rate']['min']:
                messages.append("Heart rate too low")
            elif heart_rate > self.thresholds['heart_rate']['max']:
                messages.append("Heart rate too high")

            return " | ".join(messages)

        except Exception as e:
            logger.error(f"Error generating alert message: {str(e)}")
            return "Alert condition detected"

    def _save_alert(self, user_email: str, level: str, message: str, metrics: Dict):
        """Save alert to Firebase"""
        try:
            alert_ref = self.db.collection('alerts').document(user_email)
            alert_ref.collection('history').add({
                'level': level,
                'message': message,
                'metrics': metrics,
                'timestamp': datetime.utcnow()
            })
        except Exception as e:
            logger.error(f"Error saving alert: {str(e)}")

    def _emit_alert(self, level: str, message: str):
        """Emit alert through Socket.IO"""
        try:
            emit('alert', {
                'level': level,
                'message': message,
                'timestamp': datetime.utcnow().isoformat()
            })
        except Exception as e:
            logger.error(f"Error emitting alert: {str(e)}") 
from typing import Dict, Union, Optional
import re

class MetricsValidator:
    @staticmethod
    def validate_heart_rate(value: str) -> bool:
        try:
            hr = int(value)
            return 30 <= hr <= 200  # Normal human heart rate range
        except ValueError:
            return False

    @staticmethod
    def validate_blink_rate(value: str) -> bool:
        pattern = r'^\d+/min$'
        if not re.match(pattern, value):
            return False
        rate = int(value.split('/')[0])
        return 5 <= rate <= 30  # Normal blink rate range

    @staticmethod
    def validate_eye_closure(value: str) -> bool:
        pattern = r'^\d+\.\d+s$'
        if not re.match(pattern, value):
            return False
        duration = float(value.replace('s', ''))
        return 0 <= duration <= 1.0  # Normal eye closure range

    @staticmethod
    def validate_head_position(value: str) -> bool:
        valid_positions = ['Centered', 'Left', 'Right', 'Down', 'Up']
        return value in valid_positions

    @staticmethod
    def sanitize_metrics(metrics: Dict) -> Dict:
        """Sanitize and validate all metrics"""
        sanitized = {}
        
        # Heart Rate
        if 'heartRate' in metrics and MetricsValidator.validate_heart_rate(metrics['heartRate']):
            sanitized['heartRate'] = metrics['heartRate']
        else:
            sanitized['heartRate'] = '0'

        # Blink Rate
        if 'blinkRate' in metrics and MetricsValidator.validate_blink_rate(metrics['blinkRate']):
            sanitized['blinkRate'] = metrics['blinkRate']
        else:
            sanitized['blinkRate'] = '0/min'

        # Eye Closure
        if 'eyeClosure' in metrics and MetricsValidator.validate_eye_closure(metrics['eyeClosure']):
            sanitized['eyeClosure'] = metrics['eyeClosure']
        else:
            sanitized['eyeClosure'] = '0.0s'

        # Head Position
        if 'headPosition' in metrics and MetricsValidator.validate_head_position(metrics['headPosition']):
            sanitized['headPosition'] = metrics['headPosition']
        else:
            sanitized['headPosition'] = 'Centered'

        return sanitized 
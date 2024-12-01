from datetime import datetime, timedelta
from typing import Dict, List
from app.utils.firebase_client import FirebaseClient
import logging

logger = logging.getLogger(__name__)

class TrendService:
    def __init__(self):
        self.db = None  # Initialize later when Firebase is ready
        self.pending_data = []
        self.cache = {}
    
    @property
    def _db(self):
        if self.db is None:
            self.db = FirebaseClient().get_db()
        return self.db

    def save_metrics_snapshot(self, user_email: str, metrics: Dict):
        """Save current metrics to Firebase"""
        try:
            trends_ref = self._db.collection('trends').document(user_email)
            trends_ref.collection('metrics').add({
                **metrics,
                'timestamp': datetime.utcnow()
            })
        except Exception as e:
            logger.error(f"Error saving metrics snapshot: {str(e)}")

    def get_metrics_history(self, user_email: str, hours: int = 24) -> List[Dict]:
        """Get historical metrics for specified duration"""
        try:
            start_time = datetime.utcnow() - timedelta(hours=hours)
            trends_ref = self._db.collection('trends').document(user_email)
            
            # Query metrics after start_time
            docs = trends_ref.collection('metrics')\
                .where('timestamp', '>=', start_time)\
                .order_by('timestamp')\
                .stream()

            return [self._format_metric(doc.to_dict()) for doc in docs]
        except Exception as e:
            logger.error(f"Error getting metrics history: {str(e)}")
            return []

    def _format_metric(self, metric: Dict) -> Dict:
        """Format metric for chart display"""
        return {
            'timestamp': metric['timestamp'].strftime('%H:%M:%S'),
            'alertness': float(metric.get('alertness', 0)),
            'heartRate': int(metric.get('heartRate', 0)),
            'blinkRate': float(metric.get('blinkRate', '0').split('/')[0]),
            'eyeClosure': float(metric.get('eyeClosure', '0').replace('s', '')),
        }

    def get_trend_data(self, user_email: str) -> Dict:
        """Get formatted trend data for charts"""
        try:
            metrics = self.get_metrics_history(user_email, hours=1)  # Last hour
            
            return {
                'labels': [m['timestamp'] for m in metrics],
                'datasets': {
                    'alertness': [m['alertness'] for m in metrics],
                    'heartRate': [m['heartRate'] for m in metrics],
                    'blinkRate': [m['blinkRate'] for m in metrics],
                    'eyeClosure': [m['eyeClosure'] for m in metrics]
                }
            }
        except Exception as e:
            logger.error(f"Error getting trend data: {str(e)}")
            return {'labels': [], 'datasets': {}} 

    def get_trend_analysis(self, user_email: str) -> Dict:
        """Get detailed trend analysis"""
        try:
            metrics = self.get_metrics_history(user_email, hours=1)
            if not metrics:
                return {}

            # Analyze alertness trends
            alertness_values = [m['alertness'] for m in metrics]
            alertness_analysis = self._analyze_trend(alertness_values, 'alertness')

            # Analyze heart rate trends
            heart_rates = [m['heartRate'] for m in metrics]
            heart_rate_analysis = self._analyze_trend(heart_rates, 'heart_rate')

            # Analyze blink rate
            blink_rates = [m['blinkRate'] for m in metrics]
            blink_analysis = self._analyze_trend(blink_rates, 'blink_rate')

            # Calculate fatigue indicators
            fatigue_score = self._calculate_fatigue_score(metrics[-10:] if len(metrics) > 10 else metrics)

            return {
                'alertness': alertness_analysis,
                'heart_rate': heart_rate_analysis,
                'blink_rate': blink_analysis,
                'fatigue_score': fatigue_score,
                'summary': self._generate_trend_summary(alertness_analysis, heart_rate_analysis, blink_analysis)
            }
        except Exception as e:
            logger.error(f"Error analyzing trends: {str(e)}")
            return {}

    def _analyze_trend(self, values: List[float], metric_type: str) -> Dict:
        """Analyze trend for a specific metric"""
        if not values:
            return {}

        try:
            current = values[-1]
            avg = sum(values) / len(values)
            min_val = min(values)
            max_val = max(values)
            
            # Calculate trend direction
            if len(values) > 1:
                recent_values = values[-5:]  # Last 5 values
                trend = (recent_values[-1] - recent_values[0]) / recent_values[0] * 100
            else:
                trend = 0

            # Determine status based on metric type
            status = self._determine_metric_status(current, avg, metric_type)

            return {
                'current': current,
                'average': avg,
                'minimum': min_val,
                'maximum': max_val,
                'trend_percentage': trend,
                'status': status,
                'variation': self._calculate_variation(values)
            }
        except Exception as e:
            logger.error(f"Error analyzing {metric_type} trend: {str(e)}")
            return {}

    def _determine_metric_status(self, current: float, average: float, metric_type: str) -> str:
        """Determine status based on metric type and values"""
        thresholds = {
            'alertness': {'low': 60, 'high': 80},
            'heart_rate': {'low': 60, 'high': 100},
            'blink_rate': {'low': 10, 'high': 30}
        }

        if metric_type not in thresholds:
            return 'unknown'

        threshold = thresholds[metric_type]
        if current < threshold['low']:
            return 'low'
        elif current > threshold['high']:
            return 'high'
        return 'normal'

    def _calculate_variation(self, values: List[float]) -> float:
        """Calculate variation coefficient"""
        if not values:
            return 0
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return (variance ** 0.5) / mean if mean != 0 else 0

    def _calculate_fatigue_score(self, recent_metrics: List[Dict]) -> Dict:
        """Calculate overall fatigue score based on recent metrics"""
        try:
            if not recent_metrics:
                return {'score': 0, 'level': 'unknown'}

            # Weight factors for each metric
            weights = {
                'alertness': 0.4,
                'blink_rate': 0.3,
                'eye_closure': 0.3
            }

            # Calculate weighted score
            total_score = 0
            for metric in recent_metrics:
                alertness_score = float(metric['alertness'])
                blink_rate_score = 100 - abs(float(metric['blinkRate']) - 15) * 5  # Optimal is 15
                eye_closure_score = 100 - float(metric['eyeClosure']) * 200  # Lower is better

                total_score += (
                    alertness_score * weights['alertness'] +
                    blink_rate_score * weights['blink_rate'] +
                    eye_closure_score * weights['eye_closure']
                )

            avg_score = total_score / len(recent_metrics)
            
            # Determine fatigue level
            level = 'normal' if avg_score >= 80 else 'moderate' if avg_score >= 60 else 'high'

            return {
                'score': round(avg_score, 1),
                'level': level
            }
        except Exception as e:
            logger.error(f"Error calculating fatigue score: {str(e)}")
            return {'score': 0, 'level': 'error'}

    def _generate_trend_summary(self, alertness: Dict, heart_rate: Dict, blink_rate: Dict) -> str:
        """Generate human-readable trend summary"""
        try:
            summary_parts = []

            # Alertness summary
            if alertness.get('trend_percentage'):
                direction = 'increasing' if alertness['trend_percentage'] > 5 else 'decreasing' if alertness['trend_percentage'] < -5 else 'stable'
                summary_parts.append(f"Alertness is {direction}")

            # Heart rate summary
            if heart_rate.get('status'):
                summary_parts.append(f"Heart rate is {heart_rate['status']}")

            # Blink rate summary
            if blink_rate.get('status'):
                summary_parts.append(f"Blink rate is {blink_rate['status']}")

            return ' | '.join(summary_parts) if summary_parts else "Insufficient data for analysis"
        except Exception as e:
            logger.error(f"Error generating trend summary: {str(e)}")
            return "Error generating summary"

    def cleanup(self):
        """Clean up trend service resources"""
        try:
            self.save_pending_data()
            self.clear_cache()
            self.db = None
        except Exception as e:
            logger.error(f"Error cleaning up trend service: {str(e)}")

    def save_pending_data(self):
        """Save any pending data before cleanup"""
        try:
            if self.pending_data:
                for data in self.pending_data:
                    self.save_metrics_snapshot(data['user_email'], data['metrics'])
                self.pending_data.clear()
        except Exception as e:
            logger.error(f"Error saving pending data: {str(e)}")

    def clear_cache(self):
        """Clear cached trend data"""
        self.cache.clear()
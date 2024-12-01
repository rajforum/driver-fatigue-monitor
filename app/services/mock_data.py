import random
from datetime import datetime, timedelta
import json

class MockFitbitData:
    def __init__(self):
        self.start_time = datetime.now() - timedelta(hours=24)

    def get_heart_rate_data(self):
        """Mock Fitbit Heart Rate API response"""
        data = {
            "activities-heart": [{
                "dateTime": self.start_time.strftime("%Y-%m-%d"),
                "value": {
                    "customHeartRateZones": [],
                    "heartRateZones": [
                        {"caloriesOut": 2.3, "max": 91, "min": 30, "minutes": 10, "name": "Out of Range"},
                        {"caloriesOut": 3.4, "max": 127, "min": 91, "minutes": 20, "name": "Fat Burn"},
                        {"caloriesOut": 0, "max": 154, "min": 127, "minutes": 0, "name": "Cardio"},
                        {"caloriesOut": 0, "max": 220, "min": 154, "minutes": 0, "name": "Peak"}
                    ],
                    "restingHeartRate": 68
                }
            }],
            "activities-heart-intraday": {
                "dataset": self._generate_heart_rate_dataset(),
                "datasetInterval": 1,
                "datasetType": "second"
            }
        }
        return data

    def get_sleep_data(self):
        """Mock Fitbit Sleep API response"""
        data = {
            "sleep": [{
                "dateOfSleep": self.start_time.strftime("%Y-%m-%d"),
                "duration": 25200000,  # 7 hours in milliseconds
                "efficiency": 90,
                "endTime": (self.start_time + timedelta(hours=7)).strftime("%Y-%m-%dT%H:%M:%S.%f"),
                "minutesAfterWakeup": 0,
                "minutesAsleep": 420,
                "minutesAwake": 40,
                "minutesToFallAsleep": 0,
                "startTime": self.start_time.strftime("%Y-%m-%dT%H:%M:%S.%f"),
                "timeInBed": 460,
                "type": "stages",
                "levels": {
                    "summary": {
                        "deep": {"count": 4, "minutes": 85, "thirtyDayAvgMinutes": 90},
                        "light": {"count": 25, "minutes": 249, "thirtyDayAvgMinutes": 240},
                        "rem": {"count": 4, "minutes": 86, "thirtyDayAvgMinutes": 85},
                        "wake": {"count": 23, "minutes": 40, "thirtyDayAvgMinutes": 35}
                    },
                    "data": self._generate_sleep_stages()
                }
            }]
        }
        return data

    def get_activity_data(self):
        """Mock Fitbit Activity API response"""
        data = {
            "activities": [{
                "activityId": 90013,
                "activityParentId": 90013,
                "calories": random.randint(200, 400),
                "description": "Driving",
                "duration": 3600000,  # 1 hour in milliseconds
                "hasStartTime": True,
                "isFavorite": False,
                "lastModified": self.start_time.strftime("%Y-%m-%dT%H:%M:%S.%f"),
                "logId": 123456789,
                "name": "Driving",
                "startTime": self.start_time.strftime("%Y-%m-%dT%H:%M:%S.%f"),
                "steps": random.randint(0, 100)
            }],
            "goals": {
                "activeMinutes": 30,
                "caloriesOut": 2000,
                "distance": 8.05,
                "floors": 10,
                "steps": 10000
            },
            "summary": self._generate_activity_summary()
        }
        return data

    def _generate_heart_rate_dataset(self):
        """Generate realistic heart rate data points"""
        dataset = []
        base_heart_rate = 70
        time = self.start_time

        for _ in range(3600):  # One hour of second-by-second data
            # Add some natural variation
            variation = random.gauss(0, 2)  # Normal distribution with mean 0 and std dev 2
            heart_rate = max(50, min(100, base_heart_rate + variation))
            
            dataset.append({
                "time": time.strftime("%H:%M:%S"),
                "value": round(heart_rate)
            })
            time += timedelta(seconds=1)

        return dataset

    def _generate_sleep_stages(self):
        """Generate realistic sleep stage data"""
        stages = []
        time = self.start_time
        possible_stages = ["wake", "light", "deep", "rem"]
        current_stage = "light"
        
        while time < self.start_time + timedelta(hours=7):
            duration = random.randint(10, 40)  # Minutes in this stage
            stages.append({
                "dateTime": time.strftime("%Y-%m-%dT%H:%M:%S.%f"),
                "level": current_stage,
                "seconds": duration * 60
            })
            
            # Randomly change stage with some rules
            if current_stage == "deep":
                current_stage = "light"  # Deep sleep usually transitions to light
            else:
                current_stage = random.choice(possible_stages)
                
            time += timedelta(minutes=duration)
        
        return stages

    def _generate_activity_summary(self):
        """Generate realistic activity summary"""
        return {
            "activeScore": -1,
            "activityCalories": random.randint(400, 800),
            "caloriesBMR": 1600,
            "caloriesOut": random.randint(1800, 2200),
            "distances": [
                {"activity": "total", "distance": random.uniform(3.0, 8.0)},
                {"activity": "tracker", "distance": random.uniform(3.0, 8.0)},
                {"activity": "loggedActivities", "distance": 0},
                {"activity": "veryActive", "distance": random.uniform(0.5, 2.0)},
                {"activity": "moderatelyActive", "distance": random.uniform(0.5, 2.0)},
                {"activity": "lightlyActive", "distance": random.uniform(1.0, 4.0)},
                {"activity": "sedentaryActive", "distance": 0}
            ],
            "fairlyActiveMinutes": random.randint(10, 30),
            "lightlyActiveMinutes": random.randint(150, 250),
            "marginalCalories": random.randint(200, 400),
            "sedentaryMinutes": random.randint(600, 800),
            "steps": random.randint(5000, 12000),
            "veryActiveMinutes": random.randint(15, 45)
        }

def get_mock_metrics():
    """Generate mock metrics using Fitbit-like data structure"""
    mock_fitbit = MockFitbitData()
    heart_data = mock_fitbit.get_heart_rate_data()
    sleep_data = mock_fitbit.get_sleep_data()
    activity_data = mock_fitbit.get_activity_data()

    # Extract relevant metrics
    current_heart_rate = heart_data['activities-heart-intraday']['dataset'][-1]['value']
    sleep_efficiency = sleep_data['sleep'][0]['efficiency']
    activity_level = activity_data['summary']['veryActiveMinutes']

    # Calculate alertness based on sleep and activity
    alertness = min(100, sleep_efficiency + random.randint(-10, 10))

    return {
        'heartRate': str(current_heart_rate),
        'alertness': str(alertness),
        'blinkRate': f"{random.randint(10, 20)}/min",
        'yawnCount': f"{random.randint(0, 7)}/min",
        'eyeClosure': f"{random.uniform(0.1, 0.4):.1f}s",
        'headPosition': random.choice(['Centered', 'Left', 'Right', 'Up', 'Down']),
        'alertStatus': 'Normal' if alertness > 70 else 'Warning',
        'timestamp': datetime.utcnow().isoformat(),
        'raw_data': {
            'heart_rate': heart_data,
            'sleep': sleep_data,
            'activity': activity_data
        }
    } 
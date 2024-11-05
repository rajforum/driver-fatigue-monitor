# app/modules/ai_ml/fatigue_model.py
"""
We'll start by implementing the fatigue detection model, which will take input features like eye blink frequency, head tilt, and biometric data (such as heart rate and SpO2) to predict if the driver is fatigued.

Input Features: Eye movement features (blinks, eye closure), head tilt, biometric data.
Output: A fatigue score (e.g., 0-100%) or a classification (fatigued vs. alert).

This class provides methods for training (train), making predictions (predict), and saving/loading the model.
"""

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

class FatigueDetectionModel:
    def __init__(self):
        # Initialize the classifier (RandomForest for simplicity)
        self.model = RandomForestClassifier(n_estimators=100)
        self.scaler = StandardScaler()  # Standardizing data
    
    def train(self, X_train, y_train):
        """Train the fatigue detection model."""
        # Scale the features for better model performance
        X_train_scaled = self.scaler.fit_transform(X_train)
        self.model.fit(X_train_scaled, y_train)
    
    def predict(self, X):
        """Predict the fatigue level."""
        X_scaled = self.scaler.transform(X)
        prediction = self.model.predict(X_scaled)
        return prediction
    
    def predict_proba(self, X):
        """Predict probability (for fatigue score)."""
        X_scaled = self.scaler.transform(X)
        return self.model.predict_proba(X_scaled)[:, 1]  # Probability of fatigue

    def save_model(self, filename):
        """Save the trained model to disk."""
        import joblib
        joblib.dump(self.model, filename)
        joblib.dump(self.scaler, filename + '_scaler')
    
    def load_model(self, filename):
        """Load a saved model."""
        import joblib
        self.model = joblib.load(filename)
        self.scaler = joblib.load(filename + '_scaler')

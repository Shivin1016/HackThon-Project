import numpy as np
from datetime import datetime
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib
import os

# Simulated ML model (in production, train on real data)
class SafetyPredictor:
    def __init__(self):
        self.model = None
        self.load_model()
    
    def load_model(self):
        """Load trained model or create a simple one"""
        try:
            self.model = joblib.load('models/safety_model.pkl')
        except:
            # Create a simple model for demo
            self.model = RandomForestClassifier(n_estimators=10)
            # Train on dummy data
            X_dummy = np.random.rand(100, 5)
            y_dummy = np.random.randint(0, 2, 100)
            self.model.fit(X_dummy, y_dummy)
    
    def extract_features(self, lat, lng, time_of_day, history):
        """Extract features for prediction"""
        features = [
            lat,  # latitude
            lng,  # longitude
            time_of_day / 24,  # normalized time
            len(history) if history else 0,  # incident count
            np.mean([h.get('severity', 3) for h in history]) if history else 0  # avg severity
        ]
        return np.array(features).reshape(1, -1)
    
    def predict(self, features):
        """Make prediction"""
        risk_prob = self.model.predict_proba(features)[0][1]
        return float(risk_prob * 100)

# Initialize predictor
predictor = SafetyPredictor()

def predict_risk(latitude, longitude, time_of_day, historical_data):
    """
    Predict safety risk for given parameters
    
    Returns:
        risk_score (0-100), risk_level, safety_suggestions
    """
    # Extract features
    features = predictor.extract_features(
        latitude, longitude, time_of_day, historical_data
    )
    
    # Get risk score
    risk_score = predictor.predict(features)
    
    # Determine risk level
    if risk_score < 30:
        risk_level = "Low"
        color = "green"
        suggestions = [
            "Area appears safe",
            "Normal precautions recommended"
        ]
    elif risk_score < 60:
        risk_level = "Moderate"
        color = "yellow"
        suggestions = [
            "Exercise caution",
            "Stay in well-lit areas",
            "Share your location"
        ]
    elif risk_score < 80:
        risk_level = "High"
        color = "orange"
        suggestions = [
            "High risk area",
            "Avoid if possible",
            "Travel with companion",
            "Keep emergency contacts ready"
        ]
    else:
        risk_level = "Critical"
        color = "red"
        suggestions = [
            "DANGER: Avoid this area",
            "Do not travel alone",
            "Call emergency if needed",
            "Use SafeStree SOS feature"
        ]
    
    # Time-based adjustments
    hour = datetime.now().hour
    if 20 <= hour <= 5:  # Night time
        risk_score = min(100, risk_score + 15)
        suggestions.append("Night travel increases risk")
    
    return risk_score, risk_level, suggestions
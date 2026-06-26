import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

class LeaveRiskPredictor:
    def __init__(self):
        # Initialize Scikit-Learn Random Forest Classifier
        self.model = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
        self._train_model()

    def _train_model(self):
        """
        Train a Random Forest Classifier on synthetic historical data mapping
        company leave requests, available staff coverage, deadlines, and seasonal spikes.
        """
        # Set seed for reproducibility
        np.random.seed(42)
        X = []
        y = []
        
        # Generate 1000 historical leave evaluations
        for _ in range(1000):
            # Input 1: Available Staff (0 to 10 reports active on team)
            available_staff = np.random.randint(0, 11)
            
            # Input 2: Proximity to Deadline (1 to 30 days until next task due date)
            days_to_deadline = np.random.randint(1, 31)
            
            # Input 3: Season (0: Off-peak, 1: Peak project season/busy season)
            season = np.random.choice([0, 1])
            
            # Real-world business rules used to label our training set:
            # Rule A: Extreme lack of staff -> High Risk
            if available_staff <= 1:
                risk = 2 # High Risk
            # Rule B: Immediate critical deadline -> High Risk
            elif days_to_deadline <= 3:
                risk = 2 # High Risk
            # Rule C: Busy season and close deadline -> High Risk
            elif season == 1 and days_to_deadline <= 7:
                risk = 2 # High Risk
            # Rule D: Moderate staff shortages or semi-close deadlines -> Medium Risk
            elif available_staff <= 3 or days_to_deadline <= 7 or (season == 1 and days_to_deadline <= 14):
                risk = 1 # Medium Risk
            # Rule E: Adequate staff, far deadlines -> Low Risk
            else:
                risk = 0 # Low Risk
                
            X.append([available_staff, days_to_deadline, season])
            y.append(risk)
            
        # Fit Random Forest classifier
        self.model.fit(X, y)
        print("[ML ENGINE] Scikit-Learn Random Forest Classifier trained successfully.")

    def evaluate_leave(self, available_staff, days_to_deadline, season):
        """
        Evaluate leave request parameters and return Random Forest predictions.
        
        available_staff: direct reports excluding the requester who do not have overlapping approved leaves
        days_to_deadline: days until employee's closest task deadline
        season: 0 for off-peak, 1 for peak project load
        """
        feat = [[available_staff, days_to_deadline, 1 if season else 0]]
        
        # Predict class (0: Low, 1: Medium, 2: High)
        pred = self.model.predict(feat)[0]
        
        # Get class probabilities
        probs = self.model.predict_proba(feat)[0]
        
        # Map predictions to labels
        labels = {0: "Low", 1: "Medium", 2: "High"}
        risk = labels.get(pred, "Low")
        
        # Get confidence score (probability of the predicted class)
        confidence = probs[pred]
        
        recs = {
            "High": "Reject (High Risk of operations coverage or deadline collision)",
            "Medium": "Review Carefully (Moderate staffing or task deadline proximity)",
            "Low": "Safe to Approve"
        }
        
        return {
            "risk_level": risk,
            "recommendation": recs.get(risk, "Safe to Approve"),
            "is_safe": risk != "High",
            "confidence_pct": round(confidence * 100, 1),
            "low_prob": round(probs[0] * 100, 1),
            "medium_prob": round(probs[1] * 100, 1),
            "high_prob": round(probs[2] * 100, 1)
        }

# Global singleton predictor instance
predictor = LeaveRiskPredictor()

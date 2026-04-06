"""
ML Model Module
Trains RandomForestClassifier to predict workout_type and diet_type
based on user stats (age, bmi, goal, activity level)
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
import pickle
import os

# Encodings for categorical inputs
GOAL_MAP = {"fat_loss": 0, "muscle_gain": 1, "maintenance": 2}
ACTIVITY_MAP = {"sedentary": 0, "moderate": 1, "active": 2}


class RecommendationModel:
    def __init__(self):
        self.workout_model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.diet_model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.workout_encoder = LabelEncoder()
        self.diet_encoder = LabelEncoder()
        self.is_trained = False

    def _load_training_data(self):
        """Load training dataset from CSV"""
        base_dir = os.path.dirname(os.path.dirname(__file__))
        data_path = os.path.join(base_dir, "data", "training_data.csv")
        return pd.read_csv(data_path)

    def train(self):
        """Train both workout_type and diet_type classifiers"""
        df = self._load_training_data()

        # Features: age, bmi, goal_encoded, activity_encoded
        X = df[["age", "bmi", "goal_encoded", "activity_encoded"]].values

        # --- Workout Type Model ---
        y_workout = self.workout_encoder.fit_transform(df["workout_type"])
        self.workout_model.fit(X, y_workout)

        # --- Diet Type Model ---
        y_diet = self.diet_encoder.fit_transform(df["diet_type"])
        self.diet_model.fit(X, y_diet)

        self.is_trained = True
        return {"status": "trained", "samples": len(df)}

    def predict(self, age: float, bmi: float, goal: str, activity: str) -> dict:
        """
        Predict workout_type and diet_type for given user inputs.
        Returns decoded string labels.
        """
        if not self.is_trained:
            self.train()

        goal_enc = GOAL_MAP.get(goal, 2)
        activity_enc = ACTIVITY_MAP.get(activity, 1)

        X = np.array([[age, bmi, goal_enc, activity_enc]])

        workout_pred = self.workout_model.predict(X)[0]
        diet_pred = self.diet_model.predict(X)[0]

        workout_label = self.workout_encoder.inverse_transform([workout_pred])[0]
        diet_label = self.diet_encoder.inverse_transform([diet_pred])[0]

        # Get probability scores for confidence
        workout_proba = self.workout_model.predict_proba(X)[0].max()
        diet_proba = self.diet_model.predict_proba(X)[0].max()

        return {
            "workout_type": workout_label,
            "diet_type": diet_label,
            "workout_confidence": round(float(workout_proba) * 100, 1),
            "diet_confidence": round(float(diet_proba) * 100, 1),
        }


# Singleton model instance
_model_instance = None


def get_model() -> RecommendationModel:
    """Return singleton trained model"""
    global _model_instance
    if _model_instance is None:
        _model_instance = RecommendationModel()
        _model_instance.train()
    return _model_instance

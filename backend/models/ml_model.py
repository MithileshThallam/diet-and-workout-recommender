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
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
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
        """Train both workout_type and diet_type classifiers and evaluate them"""
        df = self._load_training_data()

        # Features: age, bmi, goal_encoded, activity_encoded
        X = df[["age", "bmi", "goal_encoded", "activity_encoded"]].values

        y_workout = self.workout_encoder.fit_transform(df["workout_type"])
        y_diet = self.diet_encoder.fit_transform(df["diet_type"])

        # Split data for evaluation
        X_train, X_test, y_workout_train, y_workout_test, y_diet_train, y_diet_test = train_test_split(
            X, y_workout, y_diet, test_size=0.2, random_state=42
        )

        # Train and evaluate Workout Type Model
        self.workout_model.fit(X_train, y_workout_train)
        y_workout_pred = self.workout_model.predict(X_test)
        workout_metrics = {
            "accuracy": round(accuracy_score(y_workout_test, y_workout_pred), 4),
            "precision": round(precision_score(y_workout_test, y_workout_pred, average='weighted', zero_division=0), 4),
            "recall": round(recall_score(y_workout_test, y_workout_pred, average='weighted', zero_division=0), 4),
            "f1_score": round(f1_score(y_workout_test, y_workout_pred, average='weighted', zero_division=0), 4)
        }

        # Train and evaluate Diet Type Model
        self.diet_model.fit(X_train, y_diet_train)
        y_diet_pred = self.diet_model.predict(X_test)
        diet_metrics = {
            "accuracy": round(accuracy_score(y_diet_test, y_diet_pred), 4),
            "precision": round(precision_score(y_diet_test, y_diet_pred, average='weighted', zero_division=0), 4),
            "recall": round(recall_score(y_diet_test, y_diet_pred, average='weighted', zero_division=0), 4),
            "f1_score": round(f1_score(y_diet_test, y_diet_pred, average='weighted', zero_division=0), 4)
        }
        

        self.metrics = {
            "workout_model": workout_metrics,
            "diet_model": diet_metrics
        }
        print("\n===== MODEL EVALUATION METRICS =====")

        print("\n--- Workout Model ---")
        for k, v in workout_metrics.items():
           print(f"{k.upper()}: {v}")

        print("\n--- Diet Model ---")
        for k, v in diet_metrics.items():
           print(f"{k.upper()}: {v}")

        print("====================================\n")

        # Retrain on full dataset for optimal inference performance
        self.workout_model.fit(X, y_workout)
        self.diet_model.fit(X, y_diet)

        self.is_trained = True
        return {
            "status": "trained",
            "samples": len(df),
            "metrics": self.metrics
        }

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

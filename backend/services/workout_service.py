"""
Workout Recommendation Service
Loads workouts.csv and generates a 7-day personalised workout split
based on the ML-predicted workout type and user goal/activity level.
"""

import pandas as pd
import numpy as np
import os
import random

# 7-day muscle group splits based on workout type
WORKOUT_SPLITS = {
    "strength": [
        {"day": 1, "focus": "Chest & Triceps",   "muscle_groups": ["chest", "triceps"]},
        {"day": 2, "focus": "Back & Biceps",      "muscle_groups": ["back", "biceps"]},
        {"day": 3, "focus": "Legs & Core",         "muscle_groups": ["legs", "core", "calves"]},
        {"day": 4, "focus": "Rest / Active Recovery", "muscle_groups": []},
        {"day": 5, "focus": "Shoulders & Arms",   "muscle_groups": ["shoulders", "biceps", "triceps"]},
        {"day": 6, "focus": "Full Body Strength",  "muscle_groups": ["chest", "back", "legs"]},
        {"day": 7, "focus": "Rest & Stretching",   "muscle_groups": ["full_body"]},
    ],
    "cardio": [
        {"day": 1, "focus": "Cardio Blast",        "muscle_groups": ["full_body"]},
        {"day": 2, "focus": "Low-Intensity Steady State", "muscle_groups": ["full_body"]},
        {"day": 3, "focus": "HIIT Training",       "muscle_groups": ["full_body", "legs"]},
        {"day": 4, "focus": "Active Recovery",     "muscle_groups": ["full_body"]},
        {"day": 5, "focus": "Cardio + Core",       "muscle_groups": ["full_body", "core"]},
        {"day": 6, "focus": "Interval Training",   "muscle_groups": ["full_body", "legs"]},
        {"day": 7, "focus": "Rest & Yoga",         "muscle_groups": ["full_body"]},
    ],
    "mixed": [
        {"day": 1, "focus": "Upper Body Strength", "muscle_groups": ["chest", "back", "shoulders"]},
        {"day": 2, "focus": "Cardio & Core",       "muscle_groups": ["full_body", "core"]},
        {"day": 3, "focus": "Lower Body Strength", "muscle_groups": ["legs", "calves", "core"]},
        {"day": 4, "focus": "Active Recovery",     "muscle_groups": ["full_body"]},
        {"day": 5, "focus": "Arms & Shoulders",    "muscle_groups": ["biceps", "triceps", "shoulders"]},
        {"day": 6, "focus": "HIIT + Functional",   "muscle_groups": ["full_body", "legs"]},
        {"day": 7, "focus": "Rest & Flexibility",  "muscle_groups": ["full_body"]},
    ],
}

# Difficulty level based on activity
ACTIVITY_DIFFICULTY = {
    "sedentary": "beginner",
    "moderate": "intermediate",
    "active": "advanced",
}


def load_workouts_df() -> pd.DataFrame:
    """Load and return the workouts dataset"""
    base_dir = os.path.dirname(os.path.dirname(__file__))
    path = os.path.join(base_dir, "data", "workouts.csv")
    return pd.read_csv(path)


def select_exercises(df: pd.DataFrame, muscle_groups: list,
                     difficulty: str, workout_type: str,
                     count: int = 4, seed: int = 1) -> list:
    """
    Select exercises from dataset matching:
    - Muscle group(s) for the day
    - Appropriate difficulty level
    - Workout type (strength / cardio / mixed)

    Falls back to easier difficulty if not enough exercises found.
    """
    if not muscle_groups:
        # Rest day — return yoga/flexibility exercises
        rest_df = df[df["category"].isin(["flexibility", "recovery"])].copy()
        if rest_df.empty:
            return []
        random.seed(seed)
        chosen = rest_df.sample(min(2, len(rest_df)), random_state=seed)
        return chosen.to_dict("records")

    # Filter by muscle groups
    group_df = df[df["muscle_group"].isin(muscle_groups)].copy()

    # Filter by difficulty (with fallback)
    filtered = group_df[group_df["difficulty"] == difficulty]
    if len(filtered) < count:
        # Accept easier levels too
        filtered = group_df[group_df["difficulty"].isin([difficulty, "beginner"])]
    if len(filtered) < 2:
        filtered = group_df  # last resort: use all from group

    # Filter by workout_type if possible
    type_filtered = filtered[filtered["workout_type"].isin([workout_type, "mixed"])]
    if len(type_filtered) >= count:
        filtered = type_filtered

    # Sample exercises
    n = min(count, len(filtered))
    if n == 0:
        return []

    chosen = filtered.sample(n, random_state=seed)
    return chosen[["exercise_name", "muscle_group", "category",
                   "difficulty", "sets", "reps", "duration_min",
                   "calories_burned", "description"]].to_dict("records")


def build_workout_plan(workout_type: str, activity_level: str, goal: str) -> list:
    """
    Build a 7-day workout plan based on:
    - workout_type: from ML model (strength/cardio/mixed)
    - activity_level: determines exercise difficulty
    - goal: adjusts volume/intensity
    """
    df = load_workouts_df()
    split = WORKOUT_SPLITS.get(workout_type, WORKOUT_SPLITS["mixed"])
    difficulty = ACTIVITY_DIFFICULTY.get(activity_level, "beginner")

    # Increase exercise count for muscle gain goal
    exercises_per_day = 5 if goal == "muscle_gain" else 4

    plan = []
    for day_info in split:
        is_rest = not day_info["muscle_groups"] or (
            len(day_info["muscle_groups"]) == 1 and
            "Rest" in day_info["focus"]
        )

        exercises = select_exercises(
            df,
            muscle_groups=day_info["muscle_groups"],
            difficulty=difficulty,
            workout_type=workout_type,
            count=exercises_per_day,
            seed=day_info["day"] * 7,
        )

        # Calculate estimated calories for the day
        total_cal = sum(e.get("calories_burned", 0) for e in exercises)
        total_duration = sum(e.get("duration_min", 0) for e in exercises)

        plan.append({
            "day": day_info["day"],
            "focus": day_info["focus"],
            "is_rest": is_rest,
            "exercises": exercises,
            "total_calories_burned": total_cal,
            "total_duration_min": total_duration,
        })

    return plan


def get_fitness_tips(goal: str, workout_type: str, activity_level: str) -> list:
    """Return contextual workout tips"""
    tips = []

    # Universal
    tips.append("Always warm up for 5–10 minutes before intense exercise to prevent injury.")
    tips.append("Cool down and stretch for 5 minutes after each workout session.")

    if workout_type == "strength":
        tips.append("Progressive overload is key — gradually increase weight or reps each week.")
        tips.append("Rest 48–72 hours before training the same muscle group again for recovery.")
    elif workout_type == "cardio":
        tips.append("Aim for 150+ minutes of moderate cardio per week for heart health (WHO guideline).")
        tips.append("Mix steady-state cardio with HIIT for better fat burning results.")
    else:
        tips.append("Combine strength and cardio in the same session (strength first, then cardio).")

    if goal == "fat_loss":
        tips.append("HIIT burns 25–30% more calories than steady-state cardio in the same duration.")
    elif goal == "muscle_gain":
        tips.append("Sleep 7–9 hours per night — most muscle repair and growth happens during sleep.")

    if activity_level == "sedentary":
        tips.append("Start with 3 days/week and gradually increase frequency over 4–6 weeks.")

    return tips[:6]

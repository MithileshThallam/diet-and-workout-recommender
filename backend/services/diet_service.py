"""
Diet Recommendation Service
Loads foods.csv and builds a personalized daily meal plan
matching the user's calorie target, diet preference, and ML-predicted diet type.
"""

import pandas as pd
import numpy as np
import os
import random

# Meal calorie distribution across the day
MEAL_DISTRIBUTION = {
    "breakfast": 0.25,   # 25% of daily calories
    "lunch": 0.35,       # 35% of daily calories
    "snack": 0.15,       # 15% of daily calories
    "dinner": 0.25,      # 25% of daily calories
}


def load_foods_df() -> pd.DataFrame:
    """Load and return the foods dataset"""
    base_dir = os.path.dirname(os.path.dirname(__file__))
    path = os.path.join(base_dir, "data", "foods.csv")
    df = pd.read_csv(path)
    return df


def filter_by_preference(df: pd.DataFrame, diet_preference: str) -> pd.DataFrame:
    """
    Filter foods based on user's diet preference.
    'veg' users only see vegetarian options.
    'non-veg' users see everything.
    """
    if diet_preference == "veg":
        return df[df["diet_type"] == "veg"].copy()
    else:
        # non-veg users get both veg and non-veg options
        return df.copy()


def select_meal(df: pd.DataFrame, meal_type: str,
                target_calories: float, diet_type: str,
                seed: int = None) -> dict:
    """
    Select the best food item for a given meal slot.
    Tries to match ML-predicted diet type (high_protein, low_carb, balanced).
    Falls back gracefully if no close match found.
    """
    meal_df = df[df["meal_type"] == meal_type].copy()
    if meal_df.empty:
        return None

    # Sort by protein for high_protein, or by calories proximity
    if diet_type == "high_protein":
        meal_df = meal_df.sort_values("protein", ascending=False)
    elif diet_type == "low_carb":
        meal_df = meal_df.sort_values("carbs", ascending=True)
    else:  # balanced
        meal_df["cal_diff"] = abs(meal_df["calories"] - target_calories)
        meal_df = meal_df.sort_values("cal_diff")

    # Pick from top 5 for variety (weighted random)
    top_n = min(5, len(meal_df))
    if seed is not None:
        random.seed(seed)
    chosen = meal_df.iloc[random.randint(0, top_n - 1)]

    return {
        "food_name": chosen["food_name"],
        "meal_type": meal_type,
        "calories": int(chosen["calories"]),
        "protein_g": float(chosen["protein"]),
        "carbs_g": float(chosen["carbs"]),
        "fats_g": float(chosen["fats"]),
        "category": chosen["category"],
        "diet_type": chosen["diet_type"],
    }


def build_meal_plan(target_calories: float, diet_preference: str,
                    diet_type: str, days: int = 7) -> list:
    """
    Build a multi-day meal plan.
    Each day has: breakfast, lunch, snack, dinner.
    Total calories per day ≈ target_calories.
    """
    df = load_foods_df()
    filtered_df = filter_by_preference(df, diet_preference)

    meal_plan = []

    for day in range(1, days + 1):
        daily_meals = []
        daily_total_cal = 0

        for meal_type, fraction in MEAL_DISTRIBUTION.items():
            meal_cal_target = target_calories * fraction
            meal = select_meal(
                filtered_df, meal_type, meal_cal_target,
                diet_type, seed=day * 100 + list(MEAL_DISTRIBUTION.keys()).index(meal_type)
            )
            if meal:
                daily_meals.append(meal)
                daily_total_cal += meal["calories"]

        meal_plan.append({
            "day": day,
            "meals": daily_meals,
            "total_calories": daily_total_cal,
        })

    return meal_plan


def get_nutrition_tips(goal: str, bmi_category: str, diet_type: str) -> list:
    """Generate contextual nutrition tips based on user profile"""
    tips = []

    # Universal tips
    tips.append("Drink at least 8–10 glasses of water daily to stay hydrated and support metabolism.")
    tips.append("Eat at consistent times each day to regulate your body clock and hunger hormones.")

    # BMI-based tips
    if bmi_category == "Underweight":
        tips.append("Focus on calorie-dense, nutrient-rich foods like nuts, dairy, and whole grains.")
    elif bmi_category in ["Overweight", "Obese"]:
        tips.append("Prioritise fibre-rich vegetables and legumes to stay full on fewer calories.")
        tips.append("Avoid sugary drinks and ultra-processed snacks that spike insulin levels.")

    # Goal-based tips
    if goal == "muscle_gain":
        tips.append("Consume 20–40g of protein within 45 minutes post-workout for optimal muscle synthesis.")
        tips.append("Spread protein intake evenly across 4–5 meals rather than one large portion.")
    elif goal == "fat_loss":
        tips.append("Create a sustainable 300–500 kcal deficit — avoid crash dieting which causes muscle loss.")
        tips.append("Include high-volume, low-calorie foods (salads, soups) to manage hunger effectively.")
    else:
        tips.append("Focus on whole, minimally processed Indian foods for micronutrient density.")

    # Diet type tips
    if diet_type == "high_protein":
        tips.append("Include a protein source (dal, paneer, eggs, chicken) in every meal.")
    elif diet_type == "low_carb":
        tips.append("Replace white rice and maida with brown rice, millets, or cauliflower rice.")

    return tips[:6]  # Return max 6 tips

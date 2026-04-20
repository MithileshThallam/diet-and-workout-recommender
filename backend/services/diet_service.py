"""
Diet Recommendation Service
Builds realistic multi-item meal plans that match daily calorie targets.
"""

import pandas as pd
import os
import random

# Meal calorie distribution
MEAL_DISTRIBUTION = {
    "breakfast": 0.25,
    "lunch": 0.35,
    "snack": 0.15,
    "dinner": 0.25,
}


# -------------------------------
# Load Data
# -------------------------------
def load_foods_df() -> pd.DataFrame:
    base_dir = os.path.dirname(os.path.dirname(__file__))
    path = os.path.join(base_dir, "data", "foods.csv")
    return pd.read_csv(path)


# -------------------------------
# Filter Diet Preference
# -------------------------------
def filter_by_preference(df: pd.DataFrame, diet_preference: str) -> pd.DataFrame:
    if diet_preference == "veg":
        return df[df["diet_type"] == "veg"].copy()
    return df.copy()


# -------------------------------
# Select Meal (MULTI-ITEM FIX ✅)
# -------------------------------
def select_meal(
    df: pd.DataFrame,
    meal_type: str,
    target_calories: float,
    diet_type: str,
    seed: int = None
) -> dict:

    meal_df = df[df["meal_type"] == meal_type].copy()
    if meal_df.empty:
        return None

    if seed is not None:
        random.seed(seed)

    # Shuffle for variety
    meal_df = meal_df.sample(frac=1, random_state=seed)

    # Sort based on diet type
    if diet_type == "high_protein":
        meal_df = meal_df.sort_values("protein", ascending=False)
    elif diet_type == "low_carb":
        meal_df = meal_df.sort_values("carbs", ascending=True)

    selected_items = []
    total_cal = 0
    total_protein = 0
    total_carbs = 0
    total_fats = 0

    # Add items until ~target calories reached
    for _, row in meal_df.iterrows():
        if total_cal >= target_calories * 0.9:
            break

        selected_items.append({
            "food_name": row["food_name"],
            "calories": int(row["calories"]),
            "protein_g": float(row["protein"]),
            "carbs_g": float(row["carbs"]),
            "fats_g": float(row["fats"]),
            "category": row["category"]
        })

        total_cal += row["calories"]
        total_protein += row["protein"]
        total_carbs += row["carbs"]
        total_fats += row["fats"]

    return {
        "meal_type": meal_type,
        "items": selected_items,
        "meal_calories": round(total_cal),
        "protein_g": round(total_protein, 1),
        "carbs_g": round(total_carbs, 1),
        "fats_g": round(total_fats, 1),
    }


# -------------------------------
# Build Meal Plan
# -------------------------------
def build_meal_plan(
    target_calories: float,
    diet_preference: str,
    diet_type: str,
    days: int = 7
) -> list:

    df = load_foods_df()
    df = filter_by_preference(df, diet_preference)

    meal_plan = []

    for day in range(1, days + 1):
        daily_meals = []
        daily_total_cal = 0
        daily_protein = 0
        daily_carbs = 0
        daily_fats = 0

        for idx, (meal_type, fraction) in enumerate(MEAL_DISTRIBUTION.items()):
            meal_target = target_calories * fraction

            meal = select_meal(
                df,
                meal_type,
                meal_target,
                diet_type,
                seed=day * 100 + idx
            )

            if meal:
                daily_meals.append(meal)
                daily_total_cal += meal["meal_calories"]
                daily_protein += meal["protein_g"]
                daily_carbs += meal["carbs_g"]
                daily_fats += meal["fats_g"]

        meal_plan.append({
            "day": day,
            "meals": daily_meals,
            "total_calories": round(daily_total_cal),
            "total_protein": round(daily_protein, 1),
            "total_carbs": round(daily_carbs, 1),
            "total_fats": round(daily_fats, 1),
        })

    return meal_plan


# -------------------------------
# Nutrition Tips
# -------------------------------
def get_nutrition_tips(goal: str, bmi_category: str, diet_type: str) -> list:

    tips = []

    # General
    tips.append("Drink 8–10 glasses of water daily.")
    tips.append("Eat meals at consistent times.")

    # BMI
    if bmi_category == "Underweight":
        tips.append("Increase calorie intake with nuts, dairy, and healthy fats.")
    elif bmi_category in ["Overweight", "Obese"]:
        tips.append("Focus on high-fiber foods to stay full longer.")
        tips.append("Avoid sugary drinks and processed foods.")

    # Goal
    if goal == "muscle_gain":
        tips.append("Consume protein after workouts for muscle growth.")
        tips.append("Eat protein across multiple meals.")
    elif goal == "fat_loss":
        tips.append("Maintain a calorie deficit of 300–500 kcal.")
        tips.append("Use low-calorie high-volume foods like vegetables.")
    else:
        tips.append("Maintain a balanced diet with whole foods.")

    # Diet Type
    if diet_type == "high_protein":
        tips.append("Include protein in every meal (dal, eggs, paneer, chicken).")
    elif diet_type == "low_carb":
        tips.append("Replace white rice with millets or brown rice.")

    return tips[:6]
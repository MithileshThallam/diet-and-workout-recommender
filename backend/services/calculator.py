"""
Calculator Service
Implements fitness math formulas:
- BMI (Body Mass Index)
- BMR (Basal Metabolic Rate) using Mifflin-St Jeor
- TDEE (Total Daily Energy Expenditure)
- Macro distribution based on goal (scientifically correct)
"""

# Activity multipliers
ACTIVITY_MULTIPLIERS = {
    "sedentary": 1.2,
    "moderate": 1.55,
    "active": 1.725,
}

# Calorie adjustments per goal
GOAL_CALORIE_DELTA = {
    "fat_loss": -500,
    "muscle_gain": +300,
    "maintenance": 0,
}


# -------------------------------
# BMI
# -------------------------------
def calculate_bmi(weight_kg: float, height_cm: float) -> dict:
    height_m = height_cm / 100
    bmi = weight_kg / (height_m ** 2)
    bmi = round(bmi, 2)

    if bmi < 18.5:
        category = "Underweight"
        color = "blue"
    elif bmi < 25:
        category = "Normal"
        color = "green"
    elif bmi < 30:
        category = "Overweight"
        color = "yellow"
    else:
        category = "Obese"
        color = "red"

    return {"value": bmi, "category": category, "color": color}


# -------------------------------
# BMR (Mifflin-St Jeor)
# -------------------------------
def calculate_bmr(weight_kg: float, height_cm: float, age: int, gender: str) -> float:
    base = (10 * weight_kg) + (6.25 * height_cm) - (5 * age)

    if gender.lower() == "male":
        bmr = base + 5
    else:
        bmr = base - 161

    return round(bmr, 2)


# -------------------------------
# TDEE
# -------------------------------
def calculate_tdee(bmr: float, activity_level: str) -> float:
    multiplier = ACTIVITY_MULTIPLIERS.get(activity_level, 1.55)
    return round(bmr * multiplier, 2)


# -------------------------------
# Target Calories
# -------------------------------
def calculate_target_calories(tdee: float, goal: str) -> float:
    delta = GOAL_CALORIE_DELTA.get(goal, 0)
    return round(tdee + delta, 2)


# -------------------------------
# MACROS (FIXED LOGIC ✅)
# -------------------------------
def calculate_macros(
    calories: float,
    weight_kg: float,
    goal: str,
    diet_type: str
) -> dict:
    """
    Protein is calculated using body weight (g/kg) — NOT % calories.
    Remaining calories are split into carbs & fats.
    """

    # Diet ratios (only for carbs & fats split)
    MACRO_RATIOS = {
        "high_protein": {"carbs": 0.40, "fats": 0.30},
        "low_carb": {"carbs": 0.25, "fats": 0.40},
        "balanced": {"carbs": 0.50, "fats": 0.30},
    }

    ratios = MACRO_RATIOS.get(diet_type, MACRO_RATIOS["balanced"])

    # -------------------------------
    # Step 1: Protein (based on body weight)
    # -------------------------------
    if goal == "muscle_gain":
        protein_g = weight_kg * 2.0
    elif goal == "fat_loss":
        protein_g = weight_kg * 1.8
    else:
        protein_g = weight_kg * 1.5

    # Safety cap (very important)
    protein_g = min(protein_g, weight_kg * 2.2)
    protein_g = round(protein_g, 1)

    protein_calories = protein_g * 4

    # -------------------------------
    # Step 2: Remaining calories
    # -------------------------------
    remaining_calories = calories - protein_calories

    # Prevent negative edge case
    if remaining_calories < 0:
        remaining_calories = calories * 0.6

    # -------------------------------
    # Step 3: Carbs & Fats
    # -------------------------------
    carbs_g = (remaining_calories * ratios["carbs"]) / 4
    fats_g = (remaining_calories * ratios["fats"]) / 9

    carbs_g = round(carbs_g, 1)
    fats_g = round(fats_g, 1)

    # -------------------------------
    # Percentages (for UI display)
    # -------------------------------
    protein_pct = round((protein_calories / calories) * 100)
    carbs_pct = round((carbs_g * 4 / calories) * 100)
    fats_pct = round((fats_g * 9 / calories) * 100)

    return {
        "protein_g": protein_g,
        "carbs_g": carbs_g,
        "fats_g": fats_g,
        "protein_pct": protein_pct,
        "carbs_pct": carbs_pct,
        "fats_pct": fats_pct,
    }


# -------------------------------
# MASTER FUNCTION
# -------------------------------
def get_full_stats(
    weight_kg: float,
    height_cm: float,
    age: int,
    gender: str,
    activity_level: str,
    goal: str,
    diet_type: str = "balanced"
) -> dict:

    bmi_data = calculate_bmi(weight_kg, height_cm)
    bmr = calculate_bmr(weight_kg, height_cm, age, gender)
    tdee = calculate_tdee(bmr, activity_level)
    target_cal = calculate_target_calories(tdee, goal)

    # ✅ FIX: pass weight
    macros = calculate_macros(target_cal, weight_kg, goal, diet_type)

    return {
        "bmi": bmi_data,
        "bmr": bmr,
        "tdee": tdee,
        "target_calories": target_cal,
        "macros": macros,
    }
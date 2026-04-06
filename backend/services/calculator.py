"""
Calculator Service
Implements fitness math formulas:
- BMI (Body Mass Index)
- BMR (Basal Metabolic Rate) using Mifflin-St Jeor
- TDEE (Total Daily Energy Expenditure)
- Macro distribution based on goal
"""

# Activity multipliers per Mifflin-St Jeor guidelines
ACTIVITY_MULTIPLIERS = {
    "sedentary": 1.2,       # Little or no exercise
    "moderate": 1.55,        # Exercise 3-5 days/week
    "active": 1.725,         # Exercise 6-7 days/week
}

# Calorie adjustments per goal
GOAL_CALORIE_DELTA = {
    "fat_loss": -500,        # Caloric deficit for ~0.5kg/week loss
    "muscle_gain": +300,     # Caloric surplus for lean muscle gain
    "maintenance": 0,        # Maintain current weight
}


def calculate_bmi(weight_kg: float, height_cm: float) -> dict:
    """
    BMI = weight(kg) / height(m)^2
    Returns value + classification
    """
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


def calculate_bmr(weight_kg: float, height_cm: float, age: int, gender: str) -> float:
    """
    Mifflin-St Jeor Equation:
    Men:   10*weight + 6.25*height - 5*age + 5
    Women: 10*weight + 6.25*height - 5*age - 161
    """
    base = (10 * weight_kg) + (6.25 * height_cm) - (5 * age)
    if gender.lower() == "male":
        bmr = base + 5
    else:
        bmr = base - 161
    return round(bmr, 2)


def calculate_tdee(bmr: float, activity_level: str) -> float:
    """
    TDEE = BMR * Activity Multiplier
    """
    multiplier = ACTIVITY_MULTIPLIERS.get(activity_level, 1.55)
    return round(bmr * multiplier, 2)


def calculate_target_calories(tdee: float, goal: str) -> float:
    """
    Adjust TDEE based on goal:
    - Fat loss: -500 kcal
    - Muscle gain: +300 kcal
    - Maintenance: no change
    """
    delta = GOAL_CALORIE_DELTA.get(goal, 0)
    return round(tdee + delta, 2)


def calculate_macros(calories: float, goal: str, diet_type: str) -> dict:
    """
    Calculate macronutrient targets (protein, carbs, fats) in grams.

    Ratios vary by goal and ML-predicted diet type:
    - high_protein:  P=40% C=30% F=30%
    - low_carb:      P=35% C=25% F=40%
    - balanced:      P=30% C=40% F=30%
    """
    MACRO_RATIOS = {
        "high_protein": {"protein": 0.40, "carbs": 0.30, "fats": 0.30},
        "low_carb":     {"protein": 0.35, "carbs": 0.25, "fats": 0.40},
        "balanced":     {"protein": 0.30, "carbs": 0.40, "fats": 0.30},
    }

    ratios = MACRO_RATIOS.get(diet_type, MACRO_RATIOS["balanced"])

    # Protein & carbs = 4 kcal/g | Fats = 9 kcal/g
    protein_g = round((calories * ratios["protein"]) / 4, 1)
    carbs_g = round((calories * ratios["carbs"]) / 4, 1)
    fats_g = round((calories * ratios["fats"]) / 9, 1)

    return {
        "protein_g": protein_g,
        "carbs_g": carbs_g,
        "fats_g": fats_g,
        "protein_pct": int(ratios["protein"] * 100),
        "carbs_pct": int(ratios["carbs"] * 100),
        "fats_pct": int(ratios["fats"] * 100),
    }


def get_full_stats(weight_kg: float, height_cm: float, age: int,
                   gender: str, activity_level: str, goal: str,
                   diet_type: str = "balanced") -> dict:
    """Master function - returns all computed stats"""
    bmi_data = calculate_bmi(weight_kg, height_cm)
    bmr = calculate_bmr(weight_kg, height_cm, age, gender)
    tdee = calculate_tdee(bmr, activity_level)
    target_cal = calculate_target_calories(tdee, goal)
    macros = calculate_macros(target_cal, goal, diet_type)

    return {
        "bmi": bmi_data,
        "bmr": bmr,
        "tdee": tdee,
        "target_calories": target_cal,
        "macros": macros,
    }

"""
FastAPI Routes
POST /recommend - Main endpoint to get personalised diet & workout plan
GET /health     - Health check
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Literal

from services.calculator import get_full_stats
from services.diet_service import build_meal_plan, get_nutrition_tips
from services.workout_service import build_workout_plan, get_fitness_tips
from models.ml_model import get_model

router = APIRouter()


# --- Request Schema ---
class UserInput(BaseModel):
    age: int = Field(..., ge=10, le=100, description="Age in years")
    height_cm: float = Field(..., ge=100, le=250, description="Height in centimeters")
    weight_kg: float = Field(..., ge=20, le=300, description="Weight in kilograms")
    gender: Literal["male", "female"] = "male"
    activity_level: Literal["sedentary", "moderate", "active"] = "moderate"
    goal: Literal["fat_loss", "muscle_gain", "maintenance"] = "maintenance"
    diet_preference: Literal["veg", "non-veg"] = "veg"


@router.get("/health")
def health_check():
    return {"status": "ok", "message": "AI Diet & Workout API is running"}


@router.post("/recommend")
def get_recommendations(user: UserInput):
    """
    Main recommendation endpoint.

    Flow:
    1. Calculate BMI, BMR, TDEE, target calories
    2. Use ML model to predict workout_type and diet_type
    3. Build 7-day meal plan from dataset
    4. Build 7-day workout plan from dataset
    5. Generate tips
    6. Return everything
    """
    try:
        # Step 1: Get ML predictions
        model = get_model()
        # We need BMI for ML input — calculate it first
        bmi_val = user.weight_kg / ((user.height_cm / 100) ** 2)
        ml_result = model.predict(
            age=user.age,
            bmi=round(bmi_val, 2),
            goal=user.goal,
            activity=user.activity_level,
        )

        # Step 2: Calculate all fitness stats
        stats = get_full_stats(
            weight_kg=user.weight_kg,
            height_cm=user.height_cm,
            age=user.age,
            gender=user.gender,
            activity_level=user.activity_level,
            goal=user.goal,
            diet_type=ml_result["diet_type"],
        )

        # Step 3: Build 7-day meal plan
        meal_plan = build_meal_plan(
            target_calories=stats["target_calories"],
            diet_preference=user.diet_preference,
            diet_type=ml_result["diet_type"],
            days=7,
        )

        # Step 4: Build 7-day workout plan
        workout_plan = build_workout_plan(
            workout_type=ml_result["workout_type"],
            activity_level=user.activity_level,
            goal=user.goal,
        )

        # Step 5: Generate tips
        nutrition_tips = get_nutrition_tips(
            goal=user.goal,
            bmi_category=stats["bmi"]["category"],
            diet_type=ml_result["diet_type"],
        )
        fitness_tips = get_fitness_tips(
            goal=user.goal,
            workout_type=ml_result["workout_type"],
            activity_level=user.activity_level,
        )

        # Step 6: Assemble response
        return {
            "success": True,
            "user_profile": {
                "age": user.age,
                "gender": user.gender,
                "height_cm": user.height_cm,
                "weight_kg": user.weight_kg,
                "activity_level": user.activity_level,
                "goal": user.goal,
                "diet_preference": user.diet_preference,
            },
            "ml_predictions": ml_result,
            "stats": {
                "bmi": stats["bmi"],
                "bmr": stats["bmr"],
                "tdee": stats["tdee"],
                "target_calories": stats["target_calories"],
                "macros": stats["macros"],
            },
            "diet_plan": meal_plan,
            "workout_plan": workout_plan,
            "tips": {
                "nutrition": nutrition_tips,
                "fitness": fitness_tips,
            },
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

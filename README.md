# ⚡ FitAI — AI Diet & Workout Recommendation System

A production-ready web application that generates personalised Indian diet and workout plans using real BMI/BMR/TDEE calculations and a RandomForest ML model.

---

## 🏗️ Project Structure

```
ai-diet-workout/
├── backend/
│   ├── main.py                  # FastAPI entry point
│   ├── models/
│   │   └── ml_model.py          # RandomForestClassifier (workout + diet type)
│   ├── services/
│   │   ├── calculator.py        # BMI, BMR, TDEE, macros
│   │   ├── diet_service.py      # Meal plan builder from CSV
│   │   └── workout_service.py   # 7-day workout split from CSV
│   ├── routes/
│   │   └── recommend.py         # POST /api/recommend endpoint
│   └── data/
│       ├── foods.csv            # 60+ Indian food items with nutrition
│       ├── workouts.csv         # 50 exercises with sets/reps/muscle group
│       └── training_data.csv    # ML training data
├── frontend/
│   └── index.html               # Complete dark dashboard UI
├── requirements.txt
└── README.md
```

---

## 🚀 Quick Start

### 1. Install dependencies
```bash
cd ai-diet-workout
pip install -r requirements.txt
```

### 2. Run the server
```bash
cd backend
python main.py
```

### 3. Open your browser
```
http://localhost:8000
```

---

## 🧠 How It Works

### Backend Logic

1. **BMI** = weight(kg) / height(m)²
2. **BMR** (Mifflin-St Jeor):
   - Men:   10×weight + 6.25×height − 5×age + 5
   - Women: 10×weight + 6.25×height − 5×age − 161
3. **TDEE** = BMR × Activity Multiplier (1.2 / 1.55 / 1.725)
4. **Target Calories**:
   - Fat Loss: TDEE − 500
   - Muscle Gain: TDEE + 300
   - Maintenance: TDEE
5. **ML Model** (RandomForestClassifier):
   - Input: age, BMI, goal, activity level
   - Output: workout_type (strength/cardio/mixed) + diet_type (high_protein/low_carb/balanced)

### Datasets Used
- `foods.csv` — 60+ Indian foods (idli, dal, rajma, paneer, etc.) with full macros
- `workouts.csv` — 50 exercises categorised by muscle group, difficulty, equipment
- `training_data.csv` — Synthetic training data for the ML model

---

## 📡 API

### POST /api/recommend
```json
// Request
{
  "age": 28,
  "height_cm": 170,
  "weight_kg": 70,
  "gender": "male",
  "activity_level": "moderate",
  "goal": "muscle_gain",
  "diet_preference": "veg"
}

// Response
{
  "stats": { "bmi": {...}, "bmr": 1700, "tdee": 2635, "target_calories": 2935, "macros": {...} },
  "ml_predictions": { "workout_type": "strength", "diet_type": "high_protein", ... },
  "diet_plan": [ { "day": 1, "meals": [...] }, ... ],
  "workout_plan": [ { "day": 1, "focus": "Chest & Triceps", "exercises": [...] }, ... ],
  "tips": { "nutrition": [...], "fitness": [...] }
}
```

### GET /api/health
```json
{ "status": "ok" }
```

---

## 🎨 Frontend Features
- Dark dashboard UI with lime/cyan accents
- Stats cards (BMI, BMR, TDEE, Target Calories)
- Macro distribution bar chart
- 7-day meal plan with day tabs
- 7-day workout split cards
- Expert nutrition & fitness tips
- Fully responsive (mobile-friendly)

---

## 🛠️ Tech Stack
- **Backend**: Python 3.10+, FastAPI, scikit-learn, pandas, numpy
- **Frontend**: Vanilla HTML/CSS/JS (no framework, no dependencies)
- **Database**: CSV files (easily swappable to SQLite/PostgreSQL)
- **ML**: RandomForestClassifier (two models: workout type + diet type)

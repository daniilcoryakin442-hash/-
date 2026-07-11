ACTIVITY_COEFFICIENTS = {
    "sedentary": 1.2,      # сидячий образ жизни
    "light": 1.375,        # лёгкая активность (1-3 тренировки/нед)
    "moderate": 1.55,      # средняя активность (3-5 тренировок/нед)
    "high": 1.725,         # высокая активность (6-7 тренировок/нед)
    "very_high": 1.9,      # очень высокая (физ. работа + тренировки)
}

GOAL_MULTIPLIERS = {
    "lose": 0.85,       # похудение: -15%
    "maintain": 1.0,    # поддержание
    "gain": 1.15,       # набор массы: +15%
}


def calculate_bmr(gender: str, weight: float, height: float, age: int) -> float:
    """Формула Миффлина-Сан Жеора."""
    if gender == "male":
        return 10 * weight + 6.25 * height - 5 * age + 5
    else:
        return 10 * weight + 6.25 * height - 5 * age - 161


def calculate_tdee(bmr: float, activity: str) -> float:
    return bmr * ACTIVITY_COEFFICIENTS[activity]


def calculate_calories(tdee: float, goal: str) -> float:
    return tdee * GOAL_MULTIPLIERS[goal]


def calculate_macros(calories: float) -> dict:
    """Белки 30% / Жиры 30% / Углеводы 40% от калорий."""
    protein = (calories * 0.30) / 4
    fat = (calories * 0.30) / 9
    carbs = (calories * 0.40) / 4
    return {
        "protein": round(protein, 1),
        "fat": round(fat, 1),
        "carbs": round(carbs, 1),
    }


def full_calculation(gender: str, weight: float, height: float, age: int,
                      activity: str, goal: str) -> dict:
    bmr = calculate_bmr(gender, weight, height, age)
    tdee = calculate_tdee(bmr, activity)
    calories = round(calculate_calories(tdee, goal), 1)
    macros = calculate_macros(calories)
    return {
        "calories": calories,
        "protein": macros["protein"],
        "fat": macros["fat"],
        "carbs": macros["carbs"],
    }

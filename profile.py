from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from database import get_user, save_user
from calculations import full_calculation
from keyboards.keyboards import activity_kb, goal_kb, main_menu, profile_kb
from states import ProfileForm

router = Router()

ACTIVITY_LABELS = {
    "sedentary": "Сидячий образ жизни",
    "light": "Лёгкая активность",
    "moderate": "Средняя активность",
    "high": "Высокая активность",
    "very_high": "Очень высокая активность",
}

GOAL_LABELS = {
    "lose": "Похудение",
    "maintain": "Поддержание веса",
    "gain": "Набор массы",
}

GENDER_LABELS = {
    "male": "Мужской",
    "female": "Женский",
}


# --- Анкета ---

@router.callback_query(ProfileForm.gender, F.data.startswith("gender_"))
async def process_gender(callback: CallbackQuery, state: FSMContext):
    gender = callback.data.split("_")[1]
    await state.update_data(gender=gender)
    await callback.message.edit_text("Сколько тебе лет?")
    await state.set_state(ProfileForm.age)
    await callback.answer()


@router.message(ProfileForm.age)
async def process_age(message: Message, state: FSMContext):
    if not message.text.isdigit() or not (10 <= int(message.text) <= 100):
        await message.answer("Введи возраст числом (например, 25).")
        return
    await state.update_data(age=int(message.text))
    await message.answer("Какой у тебя рост в см?")
    await state.set_state(ProfileForm.height)


@router.message(ProfileForm.height)
async def process_height(message: Message, state: FSMContext):
    try:
        height = float(message.text.replace(",", "."))
        if not (100 <= height <= 250):
            raise ValueError
    except ValueError:
        await message.answer("Введи рост числом в см (например, 175).")
        return
    await state.update_data(height=height)
    await message.answer("Какой у тебя вес в кг?")
    await state.set_state(ProfileForm.weight)


@router.message(ProfileForm.weight)
async def process_weight(message: Message, state: FSMContext):
    try:
        weight = float(message.text.replace(",", "."))
        if not (30 <= weight <= 300):
            raise ValueError
    except ValueError:
        await message.answer("Введи вес числом в кг (например, 70).")
        return
    await state.update_data(weight=weight)
    await message.answer("Какой у тебя уровень активности?", reply_markup=activity_kb())
    await state.set_state(ProfileForm.activity)


@router.callback_query(ProfileForm.activity, F.data.startswith("activity_"))
async def process_activity(callback: CallbackQuery, state: FSMContext):
    activity = callback.data.split("activity_")[1]
    await state.update_data(activity=activity)
    await callback.message.edit_text("Какая у тебя цель?", reply_markup=goal_kb())
    await state.set_state(ProfileForm.goal)
    await callback.answer()


@router.callback_query(ProfileForm.goal, F.data.startswith("goal_"))
async def process_goal(callback: CallbackQuery, state: FSMContext):
    goal = callback.data.split("goal_")[1]
    data = await state.update_data(goal=goal)

    result = full_calculation(
        gender=data["gender"],
        weight=data["weight"],
        height=data["height"],
        age=data["age"],
        activity=data["activity"],
        goal=data["goal"],
    )

    user_data = {
        "gender": data["gender"],
        "age": data["age"],
        "height": data["height"],
        "weight": data["weight"],
        "activity": data["activity"],
        "goal": data["goal"],
        "calories": result["calories"],
        "protein": result["protein"],
        "fat": result["fat"],
        "carbs": result["carbs"],
    }
    await save_user(callback.from_user.id, user_data)
    await state.clear()

    await callback.message.edit_text(
        "Профиль готов! Рассчитал твою суточную норму:\n\n"
        f"🔥 Калории: {result['calories']} ккал\n"
        f"🥩 Белки: {result['protein']} г\n"
        f"🥑 Жиры: {result['fat']} г\n"
        f"🍞 Углеводы: {result['carbs']} г\n\n"
        "Эти значения можно поправить вручную в настройках.",
        reply_markup=profile_kb(),
    )
    await callback.answer()


# --- Просмотр профиля ---

@router.callback_query(F.data == "menu_profile")
async def show_profile(callback: CallbackQuery, state: FSMContext):
    user = await get_user(callback.from_user.id)
    if not user:
        await callback.message.edit_text("Профиль не найден. Введи /start, чтобы начать.")
        await callback.answer()
        return

    text = (
        "👤 Твой профиль\n\n"
        f"Пол: {GENDER_LABELS.get(user['gender'], '—')}\n"
        f"Возраст: {user['age']} лет\n"
        f"Рост: {user['height']} см\n"
        f"Вес: {user['weight']} кг\n"
        f"Активность: {ACTIVITY_LABELS.get(user['activity'], '—')}\n"
        f"Цель: {GOAL_LABELS.get(user['goal'], '—')}\n\n"
        "🎯 Текущая норма КБЖУ:\n"
        f"🔥 Калории: {user['calories']} ккал\n"
        f"🥩 Белки: {user['protein']} г\n"
        f"🥑 Жиры: {user['fat']} г\n"
        f"🍞 Углеводы: {user['carbs']} г"
    )
    await callback.message.edit_text(text, reply_markup=profile_kb())
    await callback.answer()

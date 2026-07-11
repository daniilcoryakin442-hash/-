from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def main_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="👤 Профиль", callback_data="menu_profile")
    builder.button(text="⚙️ Настройки", callback_data="menu_settings")
    builder.button(text="🍽 Составить рацион", callback_data="menu_diet")
    builder.adjust(1)
    return builder.as_markup()


def gender_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Мужской", callback_data="gender_male")
    builder.button(text="Женский", callback_data="gender_female")
    builder.adjust(2)
    return builder.as_markup()


def activity_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Сидячий образ жизни", callback_data="activity_sedentary")
    builder.button(text="Лёгкая активность (1-3 тр/нед)", callback_data="activity_light")
    builder.button(text="Средняя активность (3-5 тр/нед)", callback_data="activity_moderate")
    builder.button(text="Высокая активность (6-7 тр/нед)", callback_data="activity_high")
    builder.button(text="Очень высокая (физ.труд + тренировки)", callback_data="activity_very_high")
    builder.adjust(1)
    return builder.as_markup()


def goal_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Похудение", callback_data="goal_lose")
    builder.button(text="Поддержание веса", callback_data="goal_maintain")
    builder.button(text="Набор массы", callback_data="goal_gain")
    builder.adjust(1)
    return builder.as_markup()


def settings_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🔄 Пересчитать по параметрам заново", callback_data="settings_recalc")
    builder.button(text="✏️ Изменить калории вручную", callback_data="edit_calories")
    builder.button(text="✏️ Изменить белки вручную", callback_data="edit_protein")
    builder.button(text="✏️ Изменить жиры вручную", callback_data="edit_fat")
    builder.button(text="✏️ Изменить углеводы вручную", callback_data="edit_carbs")
    builder.button(text="⬅️ Назад", callback_data="menu_back")
    builder.adjust(1)
    return builder.as_markup()


def back_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ Назад", callback_data="menu_back")
    builder.adjust(1)
    return builder.as_markup()


def profile_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="⚙️ Настройки", callback_data="menu_settings")
    builder.button(text="🍽 Составить рацион", callback_data="menu_diet")
    builder.adjust(1)
    return builder.as_markup()

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from database import get_user, update_field
from keyboards.keyboards import settings_menu, gender_kb, profile_kb, back_kb
from states import ProfileForm, EditField

router = Router()

FIELD_LABELS = {
    "calories": ("калории", "ккал"),
    "protein": ("белки", "г"),
    "fat": ("жиры", "г"),
    "carbs": ("углеводы", "г"),
}


@router.callback_query(F.data == "menu_settings")
async def show_settings(callback: CallbackQuery, state: FSMContext):
    user = await get_user(callback.from_user.id)
    if not user:
        await callback.message.edit_text("Сначала заполни профиль: /start")
        await callback.answer()
        return
    await callback.message.edit_text(
        "⚙️ Настройки\n\nЗдесь можно пересчитать норму заново по параметрам "
        "или поправить любое значение вручную.",
        reply_markup=settings_menu(),
    )
    await callback.answer()


@router.callback_query(F.data == "settings_recalc")
async def recalc_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "Пересчитаем норму заново. Укажи свой пол:",
        reply_markup=gender_kb(),
    )
    await state.set_state(ProfileForm.gender)
    await callback.answer()


@router.callback_query(F.data.startswith("edit_"))
async def edit_field_start(callback: CallbackQuery, state: FSMContext):
    field = callback.data.split("edit_")[1]
    label, unit = FIELD_LABELS[field]
    await state.update_data(edit_field=field)
    await callback.message.edit_text(
        f"Введи новое значение для «{label}» (в {unit}), число:",
        reply_markup=back_kb(),
    )
    await state.set_state(EditField.waiting_value)
    await callback.answer()


@router.message(EditField.waiting_value)
async def edit_field_save(message: Message, state: FSMContext):
    try:
        value = float(message.text.replace(",", "."))
        if value <= 0 or value > 10000:
            raise ValueError
    except ValueError:
        await message.answer("Введи корректное положительное число.")
        return

    data = await state.get_data()
    field = data["edit_field"]
    label, unit = FIELD_LABELS[field]

    await update_field(message.from_user.id, field, round(value, 1))
    await state.clear()

    await message.answer(
        f"Готово! {label.capitalize()} обновлены: {round(value, 1)} {unit}.",
        reply_markup=profile_kb(),
    )

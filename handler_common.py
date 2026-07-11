from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from database import get_user
from keyboards import main_menu, gender_kb
from states import ProfileForm

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    user = await get_user(message.from_user.id)
    if user:
        await message.answer(
            "С возвращением! Что делаем?",
            reply_markup=main_menu(),
        )
    else:
        await message.answer(
            "Привет! Я помогу составлять ежедневный рацион питания под твои "
            "КБЖУ (калории, белки, жиры, углеводы).\n\n"
            "Для начала заполним профиль. Укажи свой пол:",
            reply_markup=gender_kb(),
        )
        await state.set_state(ProfileForm.gender)


@router.callback_query(F.data == "menu_back")
async def menu_back(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("Главное меню:", reply_markup=main_menu())
    await callback.answer()

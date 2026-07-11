from aiogram.fsm.state import State, StatesGroup


class ProfileForm(StatesGroup):
    gender = State()
    age = State()
    height = State()
    weight = State()
    activity = State()
    goal = State()


class EditField(StatesGroup):
    waiting_value = State()

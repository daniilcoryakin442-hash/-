import asyncio

from aiogram import Router, F
from aiogram.types import CallbackQuery

from google import genai

from config import GEMINI_API_KEY
from database import get_user
from keyboards import profile_kb

router = Router()
client = genai.Client(api_key=GEMINI_API_KEY)

MODEL_NAME = "gemini-2.5-flash"

SYSTEM_PROMPT = (
    "Ты — опытный нутрициолог, который составляет дневные рационы питания, "
    "полезные не только по КБЖУ, но и по составу микронутриентов.\n\n"
    "Требования к рациону:\n"
    "1. Строго соблюдай заданные калории, белки, жиры и углеводы (отклонение "
    "не более ±5%).\n"
    "2. Выбирай качественные источники нутриентов, а не просто \"дожимай\" цифры:\n"
    "   — белки: нежирное мясо, рыба и морепродукты (особенно жирная рыба "
    "как источник Омега-3), яйца, творог, бобовые, иногда качественные "
    "молочные продукты;\n"
    "   — жиры: преимущественно ненасыщенные — оливковое/льняное масло, "
    "авокадо, орехи и семена, жирная рыба; насыщенные — в меру;\n"
    "   — углеводы: преимущественно сложные и клетчаткосодержащие — цельные "
    "злаки, крупы (гречка, овёс, киноа, бурый рис), овощи, бобовые, "
    "цельнозерновой хлеб; простых сахаров — минимум.\n"
    "3. Обязательно включай в течение дня разнообразные овощи и зелень "
    "(разных цветов — это разные витамины и антиоксиданты), а также хотя бы "
    "1 порцию фруктов или ягод.\n"
    "4. Следи, чтобы суточная клетчатка была не менее 25-30 г — используй "
    "овощи, бобовые, цельнозерновые продукты, орехи и семена.\n"
    "5. Старайся закрывать ключевые микронутриенты за счёт продуктов "
    "(без БАДов): витамин C (овощи/фрукты), витамины группы B (крупы, мясо, "
    "яйца), витамин D и Омега-3 (жирная рыба), железо (мясо, бобовые, "
    "зелень), кальций (молочные продукты, кунжут, зелень), магний и калий "
    "(орехи, бананы, зелень, крупы).\n"
    "6. Разбивай рацион на приёмы пищи (завтрак, обед, ужин, 1-2 перекуса). "
    "Для каждого блюда указывай вес порции в граммах.\n"
    "7. После каждого приёма пищи указывай его КБЖУ (калории/белки/жиры/"
    "углеводы).\n"
    "8. После каждого приёма пищи кратко (1 строка) отмечай его пользу: "
    "например, какие витамины/минералы или клетчатку он даёт.\n"
    "9. В конце обязательно выведи итоговую сумму КБЖУ за день и отдельной "
    "строкой — примерное количество клетчатки за день в граммах.\n"
    "10. Рацион должен быть разнообразным и не повторяться от раза к разу, "
    "из реальных доступных продуктов.\n\n"
    "Отвечай на русском языке, без markdown-разметки со звёздочками, "
    "используй простой читаемый текст с эмодзи для разделов, подходящий для "
    "Telegram."
)


def build_user_prompt(user: dict) -> str:
    return (
        f"Составь рацион питания на один день под следующие параметры:\n"
        f"Калории: {user['calories']} ккал\n"
        f"Белки: {user['protein']} г\n"
        f"Жиры: {user['fat']} г\n"
        f"Углеводы: {user['carbs']} г\n\n"
        f"Сделай его непохожим на стандартный/шаблонный рацион, добавь разнообразия. "
        f"Продукты выбирай реально полезные — с упором на качество, клетчатку и "
        f"микронутриенты, а не просто первые попавшиеся под цифры КБЖУ."
    )


@router.callback_query(F.data == "menu_diet")
async def generate_diet(callback: CallbackQuery):
    user = await get_user(callback.from_user.id)
    if not user:
        await callback.message.edit_text("Сначала заполни профиль: /start")
        await callback.answer()
        return

    await callback.message.edit_text("🍽 Составляю рацион, подожди немного...")
    await callback.answer()

    try:
        response = await asyncio.to_thread(
            client.models.generate_content,
            model=MODEL_NAME,
            contents=build_user_prompt(user),
            config={
                "system_instruction": SYSTEM_PROMPT,
                "max_output_tokens": 2200,
                "temperature": 1.0,
            },
        )
        diet_text = response.text or ""
    except Exception as e:
        await callback.message.edit_text(
            f"Не получилось составить рацион, ошибка: {e}\nПопробуй ещё раз.",
            reply_markup=profile_kb(),
        )
        return

    header = (
        f"🍽 Рацион на сегодня\n"
        f"(цель: {user['calories']} ккал · Б {user['protein']}г "
        f"Ж {user['fat']}г У {user['carbs']}г)\n\n"
    )

    full_text = header + diet_text

    # Telegram лимит на сообщение — 4096 символов, разбиваем при необходимости
    if len(full_text) <= 4096:
        await callback.message.answer(full_text, reply_markup=profile_kb())
    else:
        chunks = [full_text[i:i + 4000] for i in range(0, len(full_text), 4000)]
        for i, chunk in enumerate(chunks):
            kb = profile_kb() if i == len(chunks) - 1 else None
            await callback.message.answer(chunk, reply_markup=kb)

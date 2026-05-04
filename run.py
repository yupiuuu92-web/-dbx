import subprocess
import os
import sys

print("--- ЗАПУСК СИСТЕМЫ GHOST-COMMANDER ---")

# Запускаем логгер (Flask) и перенаправляем вывод в основной терминал
logger = subprocess.Popen([sys.executable, "logger.py"], stdout=None, stderr=None)

# Запускаем бота
bot = subprocess.Popen([sys.executable, "dropdox_bot.py"], stdout=None, stderr=None)

print("--- ВСЕ ПРОЦЕССЫ ИНИЦИИРОВАНЫ ---")

try:
    logger.wait()
    bot.wait()
except KeyboardInterrupt:
    logger.terminate()
    bot.terminate()
  

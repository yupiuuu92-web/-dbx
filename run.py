import subprocess
import os

# Запускаем логгер (Flask)
logger = subprocess.Popen(["python3", "logger.py"])

# Запускаем бота
bot = subprocess.Popen(["python3", "dropdox_bot.py"])

# Ждем завершения (чтобы контейнер не закрылся)
logger.wait()
bot.wait()

import os
from flask import Flask, request

app = Flask(__name__)

@app.route('/track')
def track():
    user_ip = request.remote_addr
    user_agent = request.headers.get('User-Agent')
    # В идеале здесь логика отправки данных боту или в БД
    print(f"!!! TARGET CAUGHT !!! IP: {user_ip} Device: {user_agent}")
    return "<h1>404 Not Found</h1>", 404

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

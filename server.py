import os
import threading
from flask import Flask

app = Flask(__name__)


@app.route("/")
def home():
    return "BOT is running!"


def start_bot():
    import x_bot


threading.Thread(target=start_bot, daemon=True).start()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
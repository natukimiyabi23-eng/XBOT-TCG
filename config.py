import os
from dotenv import load_dotenv

# .env を読み込む
load_dotenv()

# Discord BOTのトークン
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# 通知先チャンネルID
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

# RSS確認間隔（秒）
CHECK_INTERVAL = 300
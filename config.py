import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
CHECK_INTERVAL = 300

TEST_MODE = os.getenv("TEST_MODE", "False").lower() == "true"
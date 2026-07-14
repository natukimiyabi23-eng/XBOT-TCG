import os

from dotenv import load_dotenv


load_dotenv()


TOKEN = os.getenv("DISCORD_BOT_TOKEN")
CHANNEL_ID_TEXT = os.getenv("CHANNEL_ID")

CHECK_INTERVAL = 300

TEST_MODE = (
    os.getenv("TEST_MODE", "false").strip().lower() == "true"
)

RSSHUB_BASE_URL = os.getenv(
    "RSSHUB_BASE_URL",
    "http://localhost:1200"
).rstrip("/")


if not TOKEN:
    raise ValueError(
        "DISCORD_BOT_TOKENが設定されていません。"
        ".envまたはRenderの環境変数を確認してください。"
    )

if not CHANNEL_ID_TEXT:
    raise ValueError(
        "CHANNEL_IDが設定されていません。"
        ".envまたはRenderの環境変数を確認してください。"
    )

try:
    CHANNEL_ID = int(CHANNEL_ID_TEXT)

except ValueError as error:
    raise ValueError(
        "CHANNEL_IDは数字だけで設定してください。"
    ) from error
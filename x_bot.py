import discord
import feedparser
from config import TOKEN, CHANNEL_ID

def load_accounts():
    accounts = []

    with open("accounts.txt", "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if not line:
                continue

            name, rss_url = line.split("|")

            accounts.append({
                "name": name,
                "rss_url": rss_url
            })

    return accounts
    

accounts = load_accounts()

print("===== RSS一覧 =====")

for account in accounts:

    print()
    print("================================")
    print("名前:", account["name"])
    print("RSS:", account["rss_url"])

    feed = feedparser.parse(account["rss_url"])

    latest_post = feed.entries[0]

    print("最新記事")

    print("タイトル:", latest_post.title)

    print("リンク:", latest_post.link)

    print("===================")
client = discord.Client(intents=discord.Intents.default())


@client.event
async def on_ready():
    print(f"ログイン成功！ {client.user} として接続しました！")

    channel = client.get_channel(CHANNEL_ID)

    if channel is None:
        print("チャンネルが見つかりません。CHANNEL_IDを確認してください。")
        return

    await channel.send("テスト通知です！BOTから送信できています。")


client.run(TOKEN)
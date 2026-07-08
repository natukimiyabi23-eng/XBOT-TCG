import discord
from discord.ext import tasks

from config import TOKEN, CHANNEL_ID, CHECK_INTERVAL, TEST_MODE
from rss_reader import fetch_posts
from storage import load_seen_posts, save_seen_posts, is_first_run
from discord_sender import send_post


def load_accounts():
    accounts = []

    with open("accounts.txt", "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if not line:
                continue

            name, rss_url = line.split("|", 1)

            accounts.append({
                "name": name,
                "rss_url": rss_url
            })

    return accounts


intents = discord.Intents.default()
client = discord.Client(intents=intents)

seen_posts = load_seen_posts()
accounts = load_accounts()
first_run = is_first_run()


@tasks.loop(seconds=CHECK_INTERVAL)
async def check_posts():
    global first_run

    channel = client.get_channel(CHANNEL_ID)

    if channel is None:
        print("チャンネルが見つかりません。CHANNEL_IDを確認してください。")
        return

    print("RSSチェック中...")

    for account in accounts:
        try:
            posts = fetch_posts(account)
            if TEST_MODE and posts:
                await send_post(channel, posts[0])
                print(f"TEST_MODE: {account['name']} の最新1件を送信しました")
                continue

            if first_run:
                for post in posts:
                    seen_posts.add(post["id"])

                print(f"{account['name']} の既存ポストを記録しました")
                continue

            new_posts = []

            for post in posts:
                if post["id"] not in seen_posts:
                    new_posts.append(post)

            for post in reversed(new_posts):
                await send_post(channel, post)

                seen_posts.add(post["id"])

            if new_posts:
                print(f"{account['name']}：{len(new_posts)}件通知しました")
            else:
                print(f"{account['name']}：新着なし")

        except Exception as e:
            print(f"{account['name']} の取得中にエラー:", e)

    save_seen_posts(seen_posts)
    first_run = False


@check_posts.before_loop
async def before_check_posts():
    await client.wait_until_ready()


@client.event
async def on_ready():
    print(f"ログイン成功！ {client.user} として接続しました！")

    if not check_posts.is_running():
        check_posts.start()


client.run(TOKEN)
import discord
from discord.ext import tasks

from config import (
    TOKEN,
    CHANNEL_ID,
    CHECK_INTERVAL,
    TEST_MODE,
    RSSHUB_BASE_URL
)
from rss_reader import fetch_posts
from storage import (
    load_seen_posts,
    save_seen_posts,
    is_first_run
)
from discord_sender import send_post


def create_rsshub_twitter_url(username):
    """
    Xのユーザー名からRSSHubのURLを作る。

    例:
    Genshin_7
    ↓
    https://my-rsshub.example.com/twitter/user/Genshin_7
    """

    username = username.strip()

    # @Genshin_7と書いても動くようにする
    username = username.lstrip("@")

    return (
        f"{RSSHUB_BASE_URL}/twitter/user/{username}"
    )


def load_accounts():
    """
    accounts.txtから監視先を読み込む。

    対応形式:

    表示名|twitter|ユーザー名
    表示名|rss|RSSのURL
    表示名|RSSのURL（旧形式）
    """

    accounts = []

    with open(
        "accounts.txt",
        "r",
        encoding="utf-8"
    ) as file:

        for line_number, line in enumerate(
            file,
            start=1
        ):
            line = line.strip()

            # 空行を無視する
            if not line:
                continue

            # #から始まるコメント行を無視する
            if line.startswith("#"):
                continue

            parts = [
                part.strip()
                for part in line.split("|")
            ]

            try:
                # 新形式:
                # 表示名|twitter|ユーザー名
                # 表示名|rss|URL
                if len(parts) == 3:
                    name = parts[0]
                    source_type = parts[1].lower()
                    source_value = parts[2]

                    if source_type == "twitter":
                        rss_url = create_rsshub_twitter_url(
                            source_value
                        )

                    elif source_type in ("rss", "atom"):
                        rss_url = source_value

                    else:
                        print(
                            f"accounts.txtの{line_number}行目: "
                            f"未対応の種類です: {source_type}",
                            flush=True
                        )
                        continue

                # 旧形式:
                # 表示名|URL
                elif len(parts) == 2:
                    name = parts[0]
                    rss_url = parts[1]

                else:
                    print(
                        f"accounts.txtの{line_number}行目: "
                        "書式が正しくありません。",
                        flush=True
                    )
                    continue

                if not name:
                    print(
                        f"accounts.txtの{line_number}行目: "
                        "表示名が空です。",
                        flush=True
                    )
                    continue

                if not rss_url:
                    print(
                        f"accounts.txtの{line_number}行目: "
                        "RSS情報が空です。",
                        flush=True
                    )
                    continue

                accounts.append({
                    "name": name,
                    "rss_url": rss_url
                })

            except Exception as error:
                print(
                    f"accounts.txtの{line_number}行目を"
                    f"読み込めませんでした: {error}",
                    flush=True
                )

    print(
        f"{len(accounts)}件の監視先を読み込みました。",
        flush=True
    )

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
        try:
            channel = await client.fetch_channel(
                CHANNEL_ID
            )

        except Exception as error:
            print(
                "Discordチャンネルの取得に失敗しました: "
                f"{error}",
                flush=True
            )
            return

    print("RSSチェック中...", flush=True)

    for account in accounts:
        try:
            posts = fetch_posts(account)

            if TEST_MODE and posts:
                await send_post(
                    channel,
                    posts[0]
                )

                print(
                    "TEST_MODE: "
                    f"{account['name']} の最新1件を"
                    "送信しました。",
                    flush=True
                )
                continue

            if first_run:
                for post in posts:
                    seen_posts.add(post["id"])

                print(
                    f"{account['name']} の既存ポストを"
                    "記録しました。",
                    flush=True
                )
                continue

            new_posts = []

            for post in posts:
                if post["id"] not in seen_posts:
                    new_posts.append(post)

            # 古い投稿から順番に送信する
            for post in reversed(new_posts):
                await send_post(
                    channel,
                    post
                )

                seen_posts.add(post["id"])

            if new_posts:
                print(
                    f"{account['name']}："
                    f"{len(new_posts)}件通知しました。",
                    flush=True
                )

            else:
                print(
                    f"{account['name']}：新着なし",
                    flush=True
                )

        except Exception as error:
            print(
                f"{account['name']} の取得中にエラー: "
                f"{type(error).__name__}: {error}",
                flush=True
            )

    save_seen_posts(seen_posts)
    first_run = False


@check_posts.before_loop
async def before_check_posts():
    await client.wait_until_ready()


@check_posts.error
async def check_posts_error(error):
    print(
        "定期監視ループでエラーが発生しました: "
        f"{type(error).__name__}: {error}",
        flush=True
    )


@client.event
async def on_ready():
    print(
        f"ログイン成功！ "
        f"{client.user} として接続しました！",
        flush=True
    )

    if not check_posts.is_running():
        check_posts.start()


client.run(TOKEN)
import discord


BOT_ICON_URL = "https://cdn-icons-png.flaticon.com/512/5968/5968958.png"

X_COLOR = 0x1DA1F2

# Embed本文に表示する最大文字数
MAX_EMBED_DESCRIPTION_LENGTH = 180


def shorten_text(text, max_length):
    """
    Discordの表示文字数を超えないように文章を短くする。
    """

    if not text:
        return ""

    text = text.strip()

    if len(text) <= max_length:
        return text

    return text[:max_length].rstrip() + "..."


def choose_display_text(post):
    """
    Embed本文に表示する文章を決める。

    RSSHubではtitleとsummaryが重複しやすいため、
    両方を表示せず、次の優先順で1つだけ表示する。

    1. summary
    2. title
    3. 本文なし
    """

    summary = post.get("summary", "").strip()
    title = post.get("title", "").strip()

    if summary:
        return shorten_text(
            summary,
            MAX_EMBED_DESCRIPTION_LENGTH
        )

    if title:
        return shorten_text(
            title,
            MAX_EMBED_DESCRIPTION_LENGTH
        )

    return ""


async def send_post(channel, post):
    """
    RSSから取得した投稿をDiscordのEmbed形式で送信する。

    RSSHubのtitleとsummaryの重複を防ぐため、
    投稿本文は1か所だけに表示する。
    """

    account_name = post.get(
        "account_name",
        "不明なアカウント"
    )

    link = post.get("link", "")
    image_url = post.get("image_url")
    published = post.get("published", "")

    description = choose_display_text(post)

    embed = discord.Embed(
        title="ポストはこちら",
        url=link if link else None,
        description=description if description else None,
        color=X_COLOR
    )

    embed.set_author(
        name=account_name,
        icon_url=BOT_ICON_URL
    )

    if image_url:
        embed.set_image(url=image_url)

    if link:
        embed.add_field(
            name="🔗 Xで見る",
            value=f"[ポストを開く]({link})",
            inline=False
        )

    if published:
        embed.set_footer(
            text=f"X通知BOT / {published}"
        )
    else:
        embed.set_footer(
            text="X通知BOT"
        )

    try:
        await channel.send(embed=embed)

    except discord.Forbidden:
        print(
            "Discordへの送信権限がありません。"
            "チャンネルまたはスレッドの権限を確認してください。",
            flush=True
        )

    except discord.NotFound:
        print(
            "送信先のチャンネルまたはスレッドが見つかりません。",
            flush=True
        )

    except discord.HTTPException as error:
        print(
            f"Discordへの送信に失敗しました: "
            f"{type(error).__name__}: {error}",
            flush=True
        )

    except Exception as error:
        print(
            f"予期しない送信エラーが発生しました: "
            f"{type(error).__name__}: {error}",
            flush=True
        )
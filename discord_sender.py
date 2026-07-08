import discord

BOT_ICON_URL = "https://cdn-icons-png.flaticon.com/512/5968/5968958.png"


async def send_post(channel, post):
    description = post["summary"]

    if description == post["title"]:
        description = ""

    embed = discord.Embed(
        title=post["title"],
        url=post["link"],
        description=description,
        color=0x1DA1F2
    )

    embed.set_author(
        name=f"{post['account_name']} の新しいポスト",
        icon_url=BOT_ICON_URL
    )

    if post.get("image_url"):
        embed.set_image(url=post["image_url"])

    embed.add_field(
        name="🔗 Xで見る",
        value=f"[ポストを開く]({post['link']})",
        inline=False
    )

    if post.get("published"):
        embed.set_footer(text=f"X通知BOT / {post['published']}")
    else:
        embed.set_footer(text="X通知BOT")

    await channel.send(embed=embed)
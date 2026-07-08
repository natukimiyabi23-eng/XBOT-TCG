import discord
from config import TOKEN, CHANNEL_ID

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
from telethon import TelegramClient, events

api_id = 123456
api_hash = "your_api_hash"

source_channels = [
    "sourcechannel1",
    "sourcechannel2"
]

target_channel = "my_news_channel"

client = TelegramClient("session", api_id, api_hash)

@client.on(events.NewMessage(chats=source_channels))
async def handler(event):
    await client.send_message(target_channel, event.message)

client.start()
client.run_until_disconnected()
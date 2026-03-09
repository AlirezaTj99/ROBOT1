import re
import asyncio
from telethon import TelegramClient, events

api_id = 123456
api_hash = "YOUR_API_HASH"

source_channels = [
    "source_channel1",
    "source_channel2"
]

target_channel = "my_channel"
my_channel_id = "@my_channel"

DELAY_BETWEEN_MESSAGES = 3

client = TelegramClient("session", api_id, api_hash)

albums = {}  # برای جمع کردن مدیاهای آلبوم


def clean_text(text):
    if not text:
        return ""

    # حذف لینک
    text = re.sub(r"http\S+", "", text)

    # حذف آیدی کانال مبدا
    text = re.sub(r"@\w+", "", text)

    return text.strip()


@client.on(events.NewMessage(chats=source_channels))
async def handler(event):

    message = event.message
    text = message.text or ""

    text = clean_text(text)

    if text:
        text = text + f"\n\n{my_channel_id}"

    # اگر پیام آلبوم باشد
    if message.grouped_id:

        albums.setdefault(message.grouped_id, [])
        albums[message.grouped_id].append(message)

        await asyncio.sleep(1)

        if len(albums[message.grouped_id]) == 1:
            await asyncio.sleep(1.5)

            media_messages = albums.pop(message.grouped_id)

            files = [m.media for m in media_messages]

            caption = text if text else f"{my_channel_id}"

            await client.send_file(
                target_channel,
                files,
                caption=caption
            )

        return

    # اگر مدیا تکی باشد
    if message.media:

        await client.send_file(
            target_channel,
            message.media,
            caption=text if text else my_channel_id
        )

    else:

        if not text:
            return

        await client.send_message(target_channel, text)

    # delay
    await asyncio.sleep(DELAY_BETWEEN_MESSAGES)


client.start()
print("Bot running...")
client.run_until_disconnected()
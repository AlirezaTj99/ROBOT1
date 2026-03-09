from telethon import TelegramClient, events
from deep_translator import GoogleTranslator
import asyncio
import re


api_id = 38981254
api_hash = "24be9fd8c44c28de5d8f0f520a6955a7"

source_channels = [
    "khabarfuri",
    "partizanfree",
    "wfwitness"
]

target_channel = "IRkhabarFory"

# my_channel_id = "🔴⭐️ اخبار جنگ | @KHABARFOOOURY"
my_channel_id = "🔴⭐️ **اخبار جنگ | @IRKHABARFORY**"

# فاصله بین ارسال پیام ها
# DELAY_BETWEEN_MESSAGES = 1

client = TelegramClient("session", api_id, api_hash)
albums = {}  # برای جمع کردن مدیاهای آلبوم

def is_persian(text):
    return re.search(r'[\u0600-\u06FF]', text)

def translate_if_english(text):

    if not text:
        return text

    # اگر فارسی باشد ترجمه نکن
    if is_persian(text):
        return text

    try:
        translated = GoogleTranslator(source='auto', target='fa').translate(text)
        return translated
    except:
        return text

def clean_text(text):
    if not text:
        return ""

    # حذف لینک ها
    text = re.sub(r"http\S+", "", text)

    # # حذف آیدی کانال ها
    text = re.sub(r'^.*@\w+.*$', '', text, flags=re.MULTILINE)

    # فیلتر تبلیغات رایج
    ad_keywords = [
        "pv",
        "vip",
        "vpn",
        "join",
        "Proxy",
        "promo",
        "discount",
        "subscribe",
        "advertisement",
        "فیلترشکن",
        "کانفیگ",
        "پروکسی",
        "دایرکت",
        "عضویت",
        "تبلیغ",
        "پی وی",
        "لینک",
        "جوین",
        "چنل",
        "بخر"
    ]

    for word in ad_keywords:
        if word.lower() in text.lower():
            return None
        
    text = translate_if_english(text)

    return text.strip()

@client.on(events.NewMessage(chats=source_channels))
async def handler(event):

    message = event.message
    text = message.text or ""

    text = clean_text(text)

    if text:
        text = f"{text} \n\n\n {my_channel_id}"
        # text = f"{text} \n\n\n <blockquote> {my_channel_id} </blockquote>"

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
                caption=caption,
                parse_mode="md"
            )

        return

    # اگر مدیا تکی باشد
    if message.media:

        await client.send_file(
            target_channel,
            message.media,
            caption=text if text else my_channel_id,
            parse_mode="md"
        )

    else:

        if not text:
            return

        await client.send_message(target_channel, text, parse_mode="md")

    # delay
    # await asyncio.sleep(DELAY_BETWEEN_MESSAGES)


client.start()
print("Bot running...")
client.run_until_disconnected()
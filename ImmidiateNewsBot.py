from telethon import TelegramClient, events
from deep_translator import GoogleTranslator
from difflib import SequenceMatcher
from collections import deque
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
my_channel_id = "🔴⭐️ **اخبار لحظه ای | @IRKHABARFORY**"

client = TelegramClient("session", api_id, api_hash)
albums = {}  # برای جمع کردن مدیاهای آلبوم


# نگهداری 50 پیام آخر
last_messages = deque(maxlen=50)
# نگهداری 50 مدیا آخر
last_media_ids = deque(maxlen=50)
SIMILARITY_THRESHOLD = 0.8


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

    # حذف سال 2026 چون درست ترنزلیت نمیشه
    text = re.sub(r"2026", "", text)

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
        "وصلم",
        "گیگی",
        "آیدی",
        "چنل",
        "بخر"
    ]

    for word in ad_keywords:
        if word.lower() in text.lower():
            return None
        
    text = translate_if_english(text)

    return text.strip()

def get_media_id(message):
    if message.photo:
        return message.photo.id
    if message.video:
        return message.video.id
    if message.document:
        return message.document.id
    return None

def is_similar(text1, text2):
    return SequenceMatcher(None, text1, text2).ratio()

def is_duplicate(text, media_id=None):
    
    # بررسی شباهت متن
    for old_text in last_messages:
        if is_similar(text, old_text) >= SIMILARITY_THRESHOLD:
            return True

    # بررسی مدیا
    if media_id and media_id in last_media_ids:
        return True

    return False

def save_recent(text, media_id):
    # ذخیره در لیست پیام‌ها
    if text:
        last_messages.append(text)

    # ذخیره مدیا
    if media_id:
        last_media_ids.append(media_id)

def MassageCheckForApp(message):
    if not message.document:
        return False

    mime = message.document.mime_type

    # چک mime type
    blocked_mimes = [
        "application/vnd.android.package-archive",
        "application/x-msdownload",
        "application/octet-stream"
    ]

    if mime in blocked_mimes:
        return True

    # چک اسم فایل
    if message.document.attributes:
        for attr in message.document.attributes:
            if hasattr(attr, "file_name"):
                name = attr.file_name.lower()
                if name.endswith((".apk", ".exe", ".ipa", ".xapk", ".msi", ".dmg")):
                    return True

    return False
        
@client.on(events.NewMessage(chats=source_channels))
async def handler(event):

    message = event.message
    
    # prevent sending App
    if MassageCheckForApp(message):
        return
    
    text = message.text or ""
    text = clean_text(text)
    media_id = get_media_id(message)


    if text:
        text = f"{text} \n\n\n {my_channel_id}"
        # text = f"{text} \n\n\n <blockquote> {my_channel_id} </blockquote>"

    # بررسی تکراری بودن
    if text and is_duplicate(text, media_id):
        return

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
            save_recent(text, media_id)

        return

    # اگر مدیا تکی باشد
    if message.media:

        # If there was no caption cancle the massage
        if not text:
            return

        await client.send_file(
            target_channel,
            message.media,
            caption=text,
            parse_mode="md"
        )
        save_recent(text, media_id)

    else:

        if not text:
            return

        await client.send_message(target_channel, text, parse_mode="md")
        save_recent(text, media_id)

client.start()
print("Bot running...")
client.run_until_disconnected()
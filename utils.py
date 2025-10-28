import yt_dlp
from aiogram import Bot
from config import CHANNELS

async def check_subscription(bot: Bot, user_id: int):
    for channel in CHANNELS:
        try:
            chat_member = await bot.get_chat_member(channel, user_id)
            if chat_member.status not in ["member", "administrator", "creator"]:
                return False
        except:
            return False
    return True

def download_media(url):
    try:
        ydl_opts = {"outtmpl": "downloads/%(title)s.%(ext)s", "quiet": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            download_url = info.get("url", None)
            title = info.get("title", "video")
        return download_url, title
    except:
        return None, None

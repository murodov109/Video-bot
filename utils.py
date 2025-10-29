import aiohttp
import os
from pathlib import Path
from config import DOWNLOADS_DIR

async def download_media(url):
    os.makedirs(DOWNLOADS_DIR, exist_ok=True)
    filename = url.split("/")[-1].split("?")[0]
    file_path = Path(DOWNLOADS_DIR) / f"{filename}.mp4"

    api_url = None

    if "tiktok" in url:
        api_url = f"https://api.tiklydown.me/api/download?url={url}"
    elif "instagram" in url:
        api_url = f"https://snapinsta.app/api.php?url={url}"
    elif "youtube" in url or "youtu.be" in url:
        api_url = f"https://api.kenliejugarap.com/api/ytdl?url={url}"
    elif "facebook" in url:
        api_url = f"https://facebook-video-downloader.fly.dev/?url={url}"

    if not api_url:
        raise Exception("Ushbu sayt qo'llab-quvvatlanmaydi.")

    async with aiohttp.ClientSession() as session:
        async with session.get(api_url) as resp:
            if resp.status != 200:
                raise Exception("API ulanishda xatolik.")
            data = await resp.json()

    video_url = None
    image_url = None

    if "download_url" in data:
        video_url = data["download_url"]
    elif "video" in data:
        video_url = data["video"]
    elif "url" in data:
        video_url = data["url"]
    elif "media" in data:
        video_url = data["media"]

    if not video_url:
        raise Exception("Video havolasi topilmadi. Havola noto‘g‘ri bo‘lishi mumkin.")

    async with aiohttp.ClientSession() as session:
        async with session.get(video_url) as resp:
            if resp.status != 200:
                raise Exception("Video faylni yuklab bo‘lmadi.")
            with open(file_path, "wb") as f:
                f.write(await resp.read())

    return str(file_path), "video"

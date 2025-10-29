import aiohttp
import os
from pathlib import Path
from config import DOWNLOADS_DIR

async def download_media(url):
    os.makedirs(DOWNLOADS_DIR, exist_ok=True)
    filename = url.split("/")[-1].split("?")[0]
    file_path = Path(DOWNLOADS_DIR) / f"{filename}.mp4"

    if "instagram.com" not in url:
        raise Exception("Faqat Instagram havolalarini qo'llab-quvvatlayman.")

    api_url = f"https://api.sssinstagram.com/api/download?url={url}"

    async with aiohttp.ClientSession() as session:
        async with session.get(api_url) as resp:
            if resp.status != 200:
                raise Exception("Instagram API bilan ulanishda xatolik.")
            data = await resp.json()

    if "url" not in data or not data["url"]:
        raise Exception("Video yoki rasm havolasi topilmadi.")

    media_url = data["url"]

    async with aiohttp.ClientSession() as session:
        async with session.get(media_url) as resp:
            if resp.status != 200:
                raise Exception("Faylni yuklab bo‘lmadi.")
            with open(file_path, "wb") as f:
                f.write(await resp.read())

    return str(file_path), "video"

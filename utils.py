import aiohttp
import os
from pathlib import Path
from config import DOWNLOADS_DIR

async def download_media(url):
    os.makedirs(DOWNLOADS_DIR, exist_ok=True)
    file_path = Path(DOWNLOADS_DIR) / "insta_media.mp4"

    if "instagram.com" not in url:
        raise Exception("Faqat Instagram havolalari qo'llab-quvvatlanadi.")

    api_url = f"https://igram.world/api/ig?url={url}"

    async with aiohttp.ClientSession() as session:
        async with session.get(api_url) as resp:
            if resp.status != 200:
                raise Exception("Instagram server bilan ulanishda xatolik.")
            data = await resp.json()

    if "data" not in data or len(data["data"]) == 0:
        raise Exception("Video yoki rasm topilmadi.")

    media_url = data["data"][0]["url"]

    async with aiohttp.ClientSession() as session:
        async with session.get(media_url) as resp:
            if resp.status != 200:
                raise Exception("Media faylni yuklab bo‘lmadi.")
            content_type = resp.headers.get("Content-Type", "")
            ext = ".jpg" if "image" in content_type else ".mp4"
            file_path = Path(DOWNLOADS_DIR) / f"insta_media{ext}"
            with open(file_path, "wb") as f:
                f.write(await resp.read())

    return str(file_path), ("photo" if file_path.suffix == ".jpg" else "video")

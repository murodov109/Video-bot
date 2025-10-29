import asyncio
import os
import yt_dlp
from pathlib import Path
from config import DOWNLOADS_DIR, DOWNLOAD_TIMEOUT

async def download_media(url):
    os.makedirs(DOWNLOADS_DIR, exist_ok=True)
    output_template = str(Path(DOWNLOADS_DIR) / "%(title)s.%(ext)s")

    ydl_opts = {
        "outtmpl": output_template,
        "format": "bestvideo+bestaudio/best",
        "merge_output_format": "mp4",
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "retries": 5,
        "geo_bypass": True,
        "age_limit": 0,
        "http_headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        },
    }

    def run_yt_dlp():
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filepath = ydl.prepare_filename(info)
            return filepath, info

    try:
        filepath, info = await asyncio.wait_for(asyncio.to_thread(run_yt_dlp), timeout=DOWNLOAD_TIMEOUT)
        ext = Path(filepath).suffix.lower()
        if info.get("ext") in ["jpg", "jpeg", "png", "webp"]:
            file_type = "photo"
        elif ext in [".mp4", ".mkv", ".mov", ".webm"]:
            file_type = "video"
        else:
            file_type = "video"
        return filepath, file_type
    except asyncio.TimeoutError:
        raise Exception("⏱ Yuklab olish vaqti tugadi.")
    except Exception as e:
        raise Exception(f"❌ Yuklab olishda xatolik: {e}")

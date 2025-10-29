import asyncio
import os
import yt_dlp
from pathlib import Path
from config import DOWNLOADS_DIR, DOWNLOAD_TIMEOUT

def _run_yt_dl(url, outtmpl):
    ydl_opts = {
        "outtmpl": outtmpl,
        "format": "bestvideo+bestaudio/best",
        "merge_output_format": "mp4",
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
    return filename

async def download_media(url):
    os.makedirs(DOWNLOADS_DIR, exist_ok=True)
    safe_template = str(Path(DOWNLOADS_DIR) / "%(title)s.%(ext)s")
    try:
        filepath = await asyncio.to_thread(_run_yt_dl, url, safe_template)
        ext = Path(filepath).suffix.lower()
        if ext in [".mp4", ".mkv", ".mov", ".webm"]:
            return filepath, "video"
        if ext in [".jpg", ".jpeg", ".png", ".webp"]:
            return filepath, "photo"
        return filepath, "video"
    except Exception as e:
        raise e

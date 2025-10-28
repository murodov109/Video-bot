import yt_dlp
import os
import aiofiles
import aiohttp

async def download_media(url):
    output_dir = "downloads"
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    try:
        ydl_opts = {
            "outtmpl": f"{output_dir}/%(title)s.%(ext)s",
            "format": "best[ext=mp4]/best",
            "quiet": True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
        ext = os.path.splitext(file_path)[1].lower()
        if ext in [".mp4", ".mov"]:
            return file_path, "video"
        elif ext in [".jpg", ".png", ".jpeg", ".webp"]:
            return file_path, "photo"
        else:
            return file_path, "video"
    except Exception as e:
        print("Download error:", e)
        raise

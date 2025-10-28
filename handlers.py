from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart
from utils import download_media
from config import ADMIN_ID, CHANNELS
import json
import os

router = Router()
USERS_FILE = "users.json"

def add_user(user_id):
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w") as f:
            json.dump([], f)
    with open(USERS_FILE, "r") as f:
        users = json.load(f)
    if user_id not in users:
        users.append(user_id)
        with open(USERS_FILE, "w") as f:
            json.dump(users, f)

def get_user_count():
    if not os.path.exists(USERS_FILE):
        return 0
    with open(USERS_FILE, "r") as f:
        return len(json.load(f))

@router.message(CommandStart())
async def start_handler(message: types.Message):
    add_user(message.from_user.id)
    text = "Salom! 👋\n\nBotdan foydalanish uchun quyidagi kanallarga obuna bo‘ling:"
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=ch, url=f"https://t.me/{ch.replace('@', '')}")]
            for ch in CHANNELS
        ] + [
            [InlineKeyboardButton(text="✅ Obuna bo‘ldim", callback_data="check_subs")]
        ]
    )
    await message.answer(text, reply_markup=keyboard)

@router.callback_query(F.data == "check_subs")
async def check_subs(call: types.CallbackQuery, bot):
    user_id = call.from_user.id
    not_subscribed = []
    for ch in CHANNELS:
        try:
            member = await bot.get_chat_member(ch, user_id)
            if member.status not in ["member", "administrator", "creator"]:
                not_subscribed.append(ch)
        except:
            not_subscribed.append(ch)
    if not not_subscribed:
        await call.message.answer("✅ Obuna tasdiqlandi!\nEndi video yoki rasm havolasini yuboring 📎")
    else:
        text = "⚠️ Quyidagi kanallarga obuna bo‘lishingiz kerak:\n\n"
        text += "\n".join(not_subscribed)
        await call.message.answer(text)

@router.message(F.text)
async def handle_link(message: types.Message):
    url = message.text.strip()
    if not any(domain in url for domain in ["tiktok.com", "youtube.com", "youtu.be", "instagram.com", "facebook.com"]):
        await message.answer("⚠️ Iltimos, TikTok, YouTube yoki Instagram havolasini yuboring.")
        return
    await message.answer("🔄 Yuklanmoqda, biroz kuting...")
    try:
        file_path, file_type = await download_media(url)
        if file_type == "video":
            await message.answer_video(types.FSInputFile(file_path))
        elif file_type == "photo":
            await message.answer_photo(types.FSInputFile(file_path))
        else:
            await message.answer("❌ Yuklab bo‘lmadi.")
    except Exception as e:
        await message.answer("❌ Xatolik yuz berdi, qayta urinib ko‘ring.")
        print(e)

@router.message(F.text == "/admin")
async def admin_panel(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return await message.answer("⛔ Siz admin emassiz.")
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📊 Statistika", callback_data="stats")],
            [InlineKeyboardButton(text="📢 Reklama yuborish", callback_data="send_ad")],
            [InlineKeyboardButton(text="📎 Majburiy obuna kanallarini boshqarish", callback_data="manage_channels")]
        ]
    )
    await message.answer("🛠 Admin panel:", reply_markup=keyboard)

@router.callback_query(F.data == "stats")
async def stats_handler(call: types.CallbackQuery):
    count = get_user_count()
    await call.message.answer(f"📊 Bot foydalanuvchilari soni: {count} ta")

@router.callback_query(F.data == "send_ad")
async def ask_ad_text(call: types.CallbackQuery):
    await call.message.answer("📢 Reklama matnini yuboring.")
    router.ad_mode = True
    router.ad_from = call.from_user.id

@router.message(F.text)
async def send_ad_to_all(message: types.Message):
    if hasattr(router, "ad_mode") and router.ad_mode and message.from_user.id == router.ad_from:
        with open(USERS_FILE, "r") as f:
            users = json.load(f)
        sent = 0
        for uid in users:
            try:
                await message.bot.send_message(uid, message.text)
                sent += 1
            except:
                pass
        router.ad_mode = False
        await message.answer(f"✅ Reklama {sent} foydalanuvchiga yuborildi.")

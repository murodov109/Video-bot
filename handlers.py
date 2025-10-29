import os
import json
import re
from pathlib import Path
from aiogram import Router, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputFile
from aiogram.filters import CommandStart
from config import ADMIN_ID, CHANNELS_FILE, USERS_FILE
from utils import download_media

router = Router()

def load_channels():
    if not os.path.exists(CHANNELS_FILE):
        with open(CHANNELS_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)
    with open(CHANNELS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_channels(channels):
    with open(CHANNELS_FILE, "w", encoding="utf-8") as f:
        json.dump(channels, f, ensure_ascii=False, indent=2)

def add_user_to_file(user_id):
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        users = json.load(f)
    if user_id not in users:
        users.append(user_id)
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, ensure_ascii=False, indent=2)

def get_user_count():
    if not os.path.exists(USERS_FILE):
        return 0
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return len(json.load(f))

admin_state = {}

URL_RE = re.compile(r"https?://[^\s]+")

@router.message(CommandStart())
async def start_cmd(message: types.Message):
    add_user_to_file(message.from_user.id)
    channels = load_channels()
    text = "Salom! 👋\n\nBotdan foydalanish uchun quyidagi kanallarga obuna bo‘ling"
    buttons = []
    for ch in channels:
        buttons.append([InlineKeyboardButton(text=ch, url=f"https://t.me/{ch.replace('@','')}")])
    buttons.append([InlineKeyboardButton(text="✅ Obuna bo‘ldim", callback_data="check_subs")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer(text, reply_markup=keyboard)

@router.callback_query(lambda c: c.data == "check_subs")
async def check_subs(call: types.CallbackQuery):
    user_id = call.from_user.id
    bot = call.message.bot
    not_subscribed = []
    channels = load_channels()
    for ch in channels:
        try:
            member = await bot.get_chat_member(ch, user_id)
            if member.status not in ("member", "administrator", "creator"):
                not_subscribed.append(ch)
        except:
            not_subscribed.append(ch)
    if not not_subscribed:
        await call.message.answer("✅ Obuna tasdiqlandi!\nEndi video yoki rasm havolasini yuboring 📎")
    else:
        text = "⚠️ Quyidagi kanallarga obuna bo‘lishingiz kerak:\n\n" + "\n".join(not_subscribed)
        await call.message.answer(text)

@router.message()
async def handle_message(message: types.Message):
    text = (message.text or "").strip()
    if not text:
        await message.answer("Iltimos, havola yuboring yoki komandadan foydalaning.")
        return
    if text.startswith("/admin"):
        if message.from_user.id != ADMIN_ID:
            await message.answer("⛔ Siz admin emassiz.")
            return
        buttons = [
            [InlineKeyboardButton(text="📊 Statistika", callback_data="stats")],
            [InlineKeyboardButton(text="📢 Reklama yuborish", callback_data="send_ad")],
            [InlineKeyboardButton(text="📎 Majburiy obuna kanallarini boshqarish", callback_data="manage_channels")]
        ]
        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
        await message.answer("🛠 Admin panel:", reply_markup=keyboard)
        return
    if message.from_user.id in admin_state:
        state = admin_state[message.from_user.id]
        if state.get("action") == "await_ad_text":
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                users = json.load(f)
            sent = 0
            for uid in users:
                try:
                    await message.bot.send_message(uid, message.text)
                    sent += 1
                except:
                    pass
            admin_state.pop(message.from_user.id, None)
            await message.answer(f"✅ Reklama {sent} foydalanuvchiga yuborildi.")
            return
        if state.get("action") == "await_add_channel":
            ch = text.strip()
            if not ch.startswith("@"):
                await message.answer("Kanal nomi @ bilan boshlanishi kerak.")
                return
            channels = load_channels()
            if ch in channels:
                await message.answer("Bu kanal allaqachon ro'yxatda.")
            else:
                channels.append(ch)
                save_channels(channels)
                await message.answer(f"✅ Kanal {ch} qo'shildi.")
            admin_state.pop(message.from_user.id, None)
            return
    match = URL_RE.search(text)
    if not match:
        await message.answer("Iltimos, haqiqiy havola yuboring.")
        return
    url = match.group(0)
    await message.answer("🔄 Yuklanmoqda, biroz kuting...")
    try:
        file_path, file_type = await download_media(url)
    except Exception as e:
        await message.answer("❌ Yuklab olishda xatolik yuz berdi.")
        return
    try:
        if file_type == "video":
            await message.answer_video(InputFile(file_path))
        elif file_type == "photo":
            await message.answer_photo(InputFile(file_path))
        else:
            await message.answer_document(InputFile(file_path))
    except Exception:
        try:
            await message.answer_document(InputFile(file_path))
        except Exception:
            await message.answer("❌ Faylni yuborib bo'lmadi.")
    try:
        Path(file_path).unlink()
    except:
        pass

@router.callback_query(lambda c: c.data == "stats")
async def stats_callback(call: types.CallbackQuery):
    if call.from_user.id != ADMIN_ID:
        await call.answer("Ruxsat yo'q", show_alert=True)
        return
    count = get_user_count()
    await call.message.answer(f"📊 Bot foydalanuvchilari soni: {count} ta")

@router.callback_query(lambda c: c.data == "send_ad")
async def send_ad_callback(call: types.CallbackQuery):
    if call.from_user.id != ADMIN_ID:
        await call.answer("Ruxsat yo'q", show_alert=True)
        return
    admin_state[call.from_user.id] = {"action": "await_ad_text"}
    await call.message.answer("📢 Reklama matnini yuboring.")

@router.callback_query(lambda c: c.data == "manage_channels")
async def manage_channels_callback(call: types.CallbackQuery):
    if call.from_user.id != ADMIN_ID:
        await call.answer("Ruxsat yo'q", show_alert=True)
        return
    channels = load_channels()
    buttons = []
    for ch in channels:
        buttons.append([InlineKeyboardButton(text=f"❌ {ch}", callback_data=f"remove_channel|{ch}")])
    buttons.append([InlineKeyboardButton(text="➕ Kanal qo'shish", callback_data="add_channel")])
    buttons.append([InlineKeyboardButton(text="🔙 Ortga", callback_data="admin_back")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await call.message.answer("📋 Majburiy kanallar boshqaruvi:", reply_markup=keyboard)

@router.callback_query(lambda c: c.data and c.data.startswith("remove_channel|"))
async def remove_channel_callback(call: types.CallbackQuery):
    if call.from_user.id != ADMIN_ID:
        await call.answer("Ruxsat yo'q", show_alert=True)
        return
    _, ch = call.data.split("|", 1)
    channels = load_channels()
    if ch in channels:
        channels.remove(ch)
        save_channels(channels)
        await call.message.answer(f"❌ Kanal {ch} ro'yxatdan o'chirildi.")
    else:
        await call.message.answer("Kanal topilmadi.")

@router.callback_query(lambda c: c.data == "add_channel")
async def add_channel_callback(call: types.CallbackQuery):
    if call.from_user.id != ADMIN_ID:
        await call.answer("Ruxsat yo'q", show_alert=True)
        return
    admin_state[call.from_user.id] = {"action": "await_add_channel"}
    await call.message.answer("🔗 Kanal nomini @ bilan yuboring (masalan @mychannel)")

@router.callback_query(lambda c: c.data == "admin_back")
async def admin_back_callback(call: types.CallbackQuery):
    if call.from_user.id != ADMIN_ID:
        await call.answer("Ruxsat yo'q", show_alert=True)
        return
    buttons = [
        [InlineKeyboardButton(text="📊 Statistika", callback_data="stats")],
        [InlineKeyboardButton(text="📢 Reklama yuborish", callback_data="send_ad")],
        [InlineKeyboardButton(text="📎 Majburiy obuna kanallarini boshqarish", callback_data="manage_channels")]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await call.message.answer("🛠 Admin panel:", reply_markup=keyboard)

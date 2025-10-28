from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart
from utils import download_media
from config import ADMIN_ID, CHANNELS

router = Router()

@router.message(CommandStart())
async def start_handler(message: types.Message):
    user_id = message.from_user.id
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

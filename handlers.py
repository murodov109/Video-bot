from aiogram import types, Bot, Router
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import ADMIN_ID
from utils import check_subscription, download_media

router = Router()

@router.message(commands=["start"])
async def start_handler(message: types.Message, bot: Bot):
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Obuna bo‘ldim", callback_data="check_sub")]
        ]
    )
    await message.answer(
        "👋 Salom! Men sizga ijtimoiy tarmoqlardan video yoki rasm yuklab beraman.\n\n"
        "Iltimos, quyidagi kanallarga obuna bo‘ling:",
        reply_markup=markup,
    )

@router.callback_query(lambda c: c.data == "check_sub")
async def check_sub_handler(callback: types.CallbackQuery, bot: Bot):
    user = callback.from_user
    is_subscribed = await check_subscription(bot, user.id)
    if is_subscribed:
        await callback.message.answer("✅ Obuna tasdiqlandi! Endi video havolasini yuboring 📎")
    else:
        await callback.message.answer("❌ Hali barcha kanallarga obuna bo‘lmadingiz.")

@router.message()
async def get_video(message: types.Message, bot: Bot):
    url = message.text
    await message.answer("🔄 Video yuklanmoqda, biroz kuting...")
    download_url, title = download_media(url)
    if not download_url:
        await message.answer("⚠️ Kechirasiz, bu havoladan video yuklab bo‘lmadi.")
        return
    try:
        await bot.send_video(message.chat.id, download_url, caption=f"🎬 {title}")
    except:
        await message.answer(f"🎞 Yuklab olish havolasi:\n{download_url}")

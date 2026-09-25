import asyncio
import logging
import sys
import html
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_TOKEN
from music_service import (
    search_music,
    download_audio,
    cleanup_file,
    telegram_file_cache
)
from web_server import start_web_server

# Log sozlamalari
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()


@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    """Start buyrug'i uchun handler."""
    user_name = message.from_user.first_name if message.from_user else "Do'stim"
    text = (
        f"👋 <b>Assalomu alaykum, {html.escape(user_name)}!</b>\n\n"
        f"🎵 Men <b>Qo'shiq qidiruvchi botman</b>.\n"
        f"Menga istalgan <b>qo'shiq nomi</b> yoki <b>ijrochi ismini</b> yozib yuboring.\n\n"
        f"⚡ Men sizga eng sara <b>Top 10</b> ta natijani topib beraman va MP3 formatida yuklab beraman!\n\n"
        f"<i>Misol uchun:</i> <code>Xamdam Sobirov</code> yoki <code>Tohir Sodiqov</code>"
    )
    await message.answer(text)


@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    """Yordam buyrug'i."""
    text = (
        "ℹ️ <b>Botdan foydalanish qo'llanmasi:</b>\n\n"
        "1️⃣ Qidirmoqchi bo'lgan qo'shiq yoki san'atkor nomini botga yozing.\n"
        "2️⃣ Bot sizga topilgan 10 ta eng yaxshi variantni ro'yxat qilib chiqaradi.\n"
        "3️⃣ Pastdagi raqamli tugmalardan birini bosing.\n"
        "4️⃣ Bot musiqani qisqa soniyalarda MP3 holida sizga yuboradi!\n\n"
        "Savollar yoki takliflar bo'lsa, adminga murojaat qiling."
    )
    await message.answer(text)


@dp.message(F.text)
async def handle_search(message: types.Message):
    """Foydalanuvchi yuborgan qo'shiq nomini qidirish."""
    query = message.text.strip()
    if not query:
        return

    # Foydalanuvchiga qidiruv boshlanganini bildirish
    status_msg = await message.answer(f"🔍 <i>«{html.escape(query)}»</i> qidirilmoqda... Kuting...")

    # Qidiruvni amalga oshirish
    results = await search_music(query, limit=10)

    if not results:
        await status_msg.edit_text(
            f"❌ Kechirasiz, <b>«{html.escape(query)}»</b> bo'yicha hech qanday qo'shiq topilmadi.\n"
            f"Iltimos, nomini to'g'ri yozib qaytadan urinib ko'ring."
        )
        return

    # Natijalar matnini shakllantirish
    text_lines = [
        f"🎧 <b>«{html.escape(query)}»</b> bo'yicha top 10 ta natija:\n"
    ]
    
    keyboard_buttons = []
    current_row = []

    for idx, item in enumerate(results, start=1):
        item_title = item.get("title", "Noma'lum")
        duration = item.get("duration_str", "")
        uploader = item.get("uploader", "")
        
        # Ro'yxat elementi
        text_lines.append(
            f"<b>{idx}.</b> 🎵 {html.escape(item_title)}\n"
            f"   ⏱ <code>{duration}</code> | 👤 <i>{html.escape(uploader)}</i>\n"
        )

        # Inline tugma: Callback data format: dl:VIDEO_ID
        video_id = item.get("id")
        btn = InlineKeyboardButton(text=f"{idx}", callback_data=f"dl:{video_id}")
        current_row.append(btn)
        
        # Har 5 ta tugmani bir qatorda joylashtirish
        if len(current_row) == 5:
            keyboard_buttons.append(current_row)
            current_row = []

    if current_row:
        keyboard_buttons.append(current_row)

    text_lines.append("👇 <b>Yuklab olish uchun kerakli raqamni bosing:</b>")
    
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
    await status_msg.edit_text("\n".join(text_lines), reply_markup=markup)


@dp.callback_query(F.data.startswith("dl:"))
async def handle_download(callback: types.CallbackQuery):
    """Tugma bosilganda musiqani yuklab yuborish."""
    video_id = callback.data.split(":", 1)[1]
    
    # Callbackni tezkor javob bilan yopish
    await callback.answer("Yuklab olish boshlandi... ⏳", show_alert=False)

    chat_id = callback.message.chat.id
    wait_msg = await callback.message.answer("⏳ <i>Musiqa tayyorlanmoqda, iltimos kuting...</i>")

    try:
        # 1. Keshda mavjudligini tekshirish (o'ta tezkor yuborish uchun)
        if video_id in telegram_file_cache:
            file_id = telegram_file_cache[video_id]
            await bot.send_audio(
                chat_id=chat_id,
                audio=file_id,
                caption="🎶 <b>@musiqazuxibot</b> orqali yuklab olindi"
            )
            await wait_msg.delete()
            return

        # 2. Serverga yuklab olish
        download_data = await download_audio(video_id)
        if not download_data or not download_data.get("file_path"):
            await wait_msg.edit_text("❌ Musiqani yuklab olishda xatolik yuz berdi. Boshqa qo'shiqni sinab ko'ring.")
            return

        file_path = download_data["file_path"]
        title = download_data.get("title", "Qo'shiq")
        uploader = download_data.get("uploader", "Noma'lum ijrochi")
        duration = download_data.get("duration", 0)

        # Telegram orqali yuborish
        audio_file = FSInputFile(file_path, filename=f"{title}.mp3")
        sent_audio = await bot.send_audio(
            chat_id=chat_id,
            audio=audio_file,
            title=title,
            performer=uploader,
            duration=int(duration) if duration else None,
            caption="🎶 <b>@musiqazuxibot</b> orqali yuklab olindi"
        )

        # File ID ni keshga saqlash (keyingi safar bir soniyada yuborish uchun)
        if sent_audio.audio:
            telegram_file_cache[video_id] = sent_audio.audio.file_id

        # Vaqtinchalik xabarni o'chirish
        await wait_msg.delete()

        # Server xotirasini tozalash (joy to'lib qolmasligi uchun)
        cleanup_file(file_path)

    except Exception as e:
        logger.error(f"Audio yuborishda xatolik: {e}")
        await wait_msg.edit_text("❌ Musiqani yuborishda xatolik yuz berdi. Birozdan so'ng qayta urinib ko'ring.")


async def main():
    """Bot va Web serverni bir vaqtda ishga tushiruvchi asosiy funksiya."""
    logger.info("Bot ishga tushirilmoqda...")
    
    # 1. Render talab qiladigan Veb serverni ishga tushirish
    await start_web_server()

    # 2. Eskirgan yangilanishlarni (updates) tozalash
    await bot.delete_webhook(drop_pending_updates=True)

    # 3. Telegram pollingni boshlash
    logger.info("Telegram Bot muvaffaqiyatli ishga tushdi va xabarlarni kutmoqda!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot to'xtatildi.")

import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import google.generativeai as genai
import aiosqlite
import os

# ================= CONFIG =================
TELEGRAM_TOKEN = ""
GEMINI_API_KEY = ""

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")
dp = Dispatcher()
bot = Bot(token=TELEGRAM_TOKEN)

# ================= DATABASE =================
DB_NAME = os.path.join("/storage/emulated/0/CareerAi", "bot.db")

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            lang TEXT
        )
        """)
        await db.commit()

async def set_user(user_id: int, username: str = None, lang: str = None):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
        INSERT INTO users (id, username, lang) 
        VALUES (?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET username=excluded.username, lang=excluded.lang
        """, (user_id, username, lang))
        await db.commit()

async def get_user(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT username, lang FROM users WHERE id=?", (user_id,)) as cursor:
            return await cursor.fetchone()

# ================= HELPERS =================
def split_message(text, chunk_size=4000):
    chunks = []
    for i in range(0, len(text), chunk_size):
        chunks.append(text[i:i + chunk_size])
    return chunks

# ================= HANDLERS =================
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    user_id = message.from_user.id

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🇦🇿 Azərbaycan dili", callback_data="lang_az")],
            [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")]
        ]
    )

    await message.answer(
        "🇦🇿AZ:\n👋 Salam! Mən CareerAI. Sənin şəxsi karyera məsləhətçinəm🤖"
        "\n\nKaryeranı rahatca qura bilmək və roadmap tövsiyələri vermək üçün burdayam🎉"
        "\nGəl ilk olaraq dilini seçək"
        "\n\n🇬🇧ENG:\n👋 Hello! I’m CareerAI. Your personal career advisor🤖"
        "\n\nI’m here to help you build your career easily and provide roadmap recommendations🎉"
        "\nLet’s start by choosing your language",
        reply_markup=keyboard
    )

@dp.callback_query()
async def lang_handler(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if callback.data == "lang_az":
        await set_user(user_id, lang="az")
        await callback.message.answer("Dil seçildi: Azərbaycan dili 🇦🇿\nİndi adını de ki, sənə necə müraciət edəcəyimi bilim☺️")
    elif callback.data == "lang_en":
        await set_user(user_id, lang="en")
        await callback.message.answer("Language selected: English 🇬🇧\nNow tell me your name so I know how to call you☺️")

@dp.message()
async def message_handler(message: types.Message):
    user_id = message.from_user.id
    user_data = await get_user(user_id)

    if not user_data:
        await message.answer("Zəhmət olmasa, əvvəlcə dili seçin / Please choose a language for start")
        return

    username, lang = user_data

    if not username:
        await set_user(user_id, username=message.text, lang=lang)
        if lang == "az":
            await message.answer(
                f"Çox gözəl, {message.text}! "
                "\nİndi mən sənə karyera məsləhətçisi kimi kömək edə bilərəm🚀"
            )
        else:
            await message.answer(
                f"Very nice, {message.text}! "
                "\nNow I can help you as a career consultant🚀"
            )
        return

    name = username
    if lang == "az":
        prompt = f"""
        Sən karyera məsləhətçisisən. İstifadəçiyə peşə seçimi, gələcək planlar,
        universitet və iş imkanları haqqında peşəkar və faydalı cavablar ver.
        Ona daim bu ad ilə xitab et: "{name}".
        İstifadəçi belə yazdı: "{message.text}".
        """
        await message.answer("Sualınızın cavabı hazırlanır♻️..")
    else:
        prompt = f"""
        You are a career advisor. Provide professional and useful answers about career choice,
        future plans, university, and job opportunities.
        Always address the user by this name: "{name}".
        The user wrote: "{message.text}".
        """
        await message.answer("Your answer is being prepared♻️..")

    # Gemini cavabını al
    response = model.generate_content(prompt)

    chunks = split_message(response.text)
    for chunk in chunks:
        await message.answer(chunk)

# ================= MAIN =================
async def main():
    await init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
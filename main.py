import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import google.generativeai as genai
import aiosqlite
from dotenv import load_dotenv

load_dotenv('/storage/emulated/0/CareerAi/.env')

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not TELEGRAM_TOKEN or not GEMINI_API_KEY:
    raise ValueError("TELEGRAM_TOKEN or GEMINI_API_KEY environment variable is not set!")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")
dp = Dispatcher()
bot = Bot(token=TELEGRAM_TOKEN)

DB_NAME = "Careerai_datas.db"

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            lang TEXT
        )
        """)
        await db.execute("""
        CREATE TABLE IF NOT EXISTS history (
            user_id INTEGER,
            role TEXT,
            content TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
        await db.commit()

async def set_user(user_id: int, username: str = None, lang: str = None):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
        INSERT INTO users (id, username, lang)
        VALUES (?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET 
            username=excluded.username,
            lang=excluded.lang
        """, (user_id, username, lang))
        await db.commit()

async def get_user(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT username, lang FROM users WHERE id=?", (user_id,)) as cursor:
            return await cursor.fetchone()

async def add_message(user_id: int, role: str, content: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("INSERT INTO history (user_id, role, content) VALUES (?, ?, ?)", 
                         (user_id, role, content))
        await db.commit()

async def get_history(user_id: int, limit: int = 10):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("""
            SELECT role, content FROM history 
            WHERE user_id=? ORDER BY timestamp DESC LIMIT ?
        """, (user_id, limit)) as cursor:
            rows = await cursor.fetchall()
            return list(reversed(rows))

def split_message(text, chunk_size=4000):
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🇦🇿 Azərbaycan dili", callback_data="lang_az")],
            [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")]
        ]
    )

    await message.answer(
        "👋 Salam! Mən CareerAI. Karyera məsləhətçinəm.\nGəl, ilk olaraq dilini seçək👇",
        reply_markup=keyboard
    )

@dp.callback_query()
async def lang_handler(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if callback.data == "lang_az":
        await set_user(user_id, lang="az")
        await callback.message.answer("Dil seçildi: Azərbaycan dili 🇦🇿\nİndi adını de ☺️")
    elif callback.data == "lang_en":
        await set_user(user_id, lang="en")
        await callback.message.answer("Language selected: English 🇬🇧\nNow tell me your name ☺️")

@dp.message()
async def message_handler(message: types.Message):
    user_id = message.from_user.id
    user_data = await get_user(user_id)

    if not user_data:
        await message.answer("Zəhmət olmasa, əvvəlcə dili seçin / Please choose a language first")
        return

    username, lang = user_data

    if not username:
        await set_user(user_id, username=message.text, lang=lang)
        if lang == "az":
            await message.answer(f"Çox gözəl, {message.text}! Başlayaq 🚀")
        else:
            await message.answer(f"Nice, {message.text}! Let's begin 🚀")
        return

    await add_message(user_id, "user", message.text)

    history = await get_history(user_id, limit=10)
    chat_history = [{"role": r, "parts": [c]} for r, c in history]

    if lang == "az":
        system_prompt =( 
            f"Sən karyera məsləhətçisisən və istifadəçiyə '{username}' adı ilə müraciət et. "
            "İstifadəçini analiz et və ona uyğun cavab ver."
        )
    else:
        system_prompt = (
            f"You are a career advisor and address the user by this name: {username}. "
            "Analyze the user and give a personalized answer."
        )

    chat = model.start_chat(
        history=[{"role": "user", "parts": [system_prompt]}] + chat_history
    )

    await message.answer("Cavab hazırlanır ♻️...")

    response = await asyncio.to_thread(chat.send_message, message.text)

    try:
        reply_text = response.text
    except AttributeError:
        reply_text = response.candidates[0].content.parts[0].text

    reply_text = reply_text.replace("*", "")
    await add_message(user_id, "model", reply_text)

    for chunk in split_message(reply_text):
        await message.answer(chunk)

async def main():
    await init_db()
    print("✅ Bot hazırdır!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()
    asyncio.run(main())
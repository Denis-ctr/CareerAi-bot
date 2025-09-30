import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import google.generativeai as genai
import aiosqlite

# CONFIG
TELEGRAM_TOKEN = ""
GEMINI_API_KEY = ""

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")
dp = Dispatcher()
bot = Bot(token=TELEGRAM_TOKEN)

# DATABASE
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
            return list(reversed(rows))  # köhnədən yeniyə doğru qaytarır

# HELPERS
def split_message(text, chunk_size=4000):
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

# HANDLERS
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🇦🇿 Azərbaycan dili", callback_data="lang_az")],
            [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en")]
        ]
    )

    await message.answer(
        "🇦🇿AZ:\n👋 Salam! Mən CareerAI. Sənin şəxsi karyera məsləhətçinəm🤖"
        "\n\nKaryeranı rahatca qura bilmək və roadmap tövsiyələri vermək üçün burdayam🥳"
        "\nGəl ilk olaraq dilini seçək"
        "\n\n🇬🇧ENG:\n👋 Hello! I’m CareerAI. Your personal career advisor🤖"
        "\n\nI’m here to help you build your career easily and provide roadmap recommendations🥳"
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
        await message.answer("Zəhmət olmasa, əvvəlcə dili seçin / Please choose a language first")
        return

    username, lang = user_data

    # Əgər ad yazılmayıbsa
    if not username:
        await set_user(user_id, username=message.text, lang=lang)
        if lang == "az":
            await message.answer(f"Çox gözəl, {message.text}! \nİndi mən sənə karyera məsləhətçisi kimi kömək edə bilərəm🚀")
        else:
            await message.answer(f"Very nice, {message.text}! \nNow I can help you as a career consultant🚀")
        return

    # userin mesajını history-yə əlavə edən kod
    await add_message(user_id, "user", message.text)

    # əvvəlki history-ni databaseden çəkmək
    history = await get_history(user_id, limit=10)
    chat_history = [{"role": r, "parts": [c]} for r, c in history]

    # dilə uyğun prompt
    if lang == "az":
        system_prompt =( 
        f"Sən karyera məsləhətçisisən və istifadəçiyə '{username}' adı ilə müraciət et."
        "İstifadəçiyə diqqət yetir və onun xarakterini analiz et."
        "Xarakterini analiz etdikdən sonra ona uyğun gelişmiş bir cavab ver."
      )
    else:
        system_prompt = (
        f"You are a career advisor and always address the user by this name: {username}."
         "describe the character of the user"
         "Next give the user a personal advice"
      )
    # Gemini chat
    chat = model.start_chat(
        history=[{"role": "user", "parts": [system_prompt]}] + chat_history
    )

    await message.answer("Cavab hazırlanır♻️..")

    response = chat.send_message(message.text)

    
    reply_text = response.text or ""
    reply_text = reply_text.replace("*", "")

    
    await add_message(user_id, "model", reply_text)

   
    for chunk in split_message(reply_text):
        await message.answer(chunk)

# MAIN
async def main():
    await init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
  
    asyncio.run(main())
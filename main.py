import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import google.generativeai as genai

# Config
TELEGRAM_TOKEN = ""
GEMINI_API_KEY = ""

# Qurulum
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")
dp = Dispatcher()
bot = Bot(token=TELEGRAM_TOKEN)

# user input
user_nm = {}

#startcommand
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    user_id = message.from_user.id
    user_nm.pop(user_id, None)  
    await message.answer(
        "👋 Salam! Mən CareerAI. Sənin şəxsi karyera məsləhətçinəm🤖"
        "\n\nKaryeranı rahatca qura bilmək və roadmap tövsiyələri vermək üçün burdayam🎉"
        "\n\nBaşlamazdan əvvəl adını de ki, sənə necə xitab edəcəyimi bilim☺️"
    )

# msghand
@dp.message()
async def message_handler(message: types.Message):
    user_id = message.from_user.id

    # ad yoxdusa əlavə et
    if user_id not in user_nm:
        user_nm[user_id] = message.text
        await message.answer(
            f"Çox gözəl, {message.text}! "
            "İndi mən sənə karyera məsləhətçisi kimi kömək edə bilərəm. "
            "İstədiyin sualı verə bilərsən☺️"
        )
        return

    # Əks-hal cavab
    name = user_nm[user_id]
    prompt = f"""
    Sən karyera məsləhətçisisən. İstifadəçiyə peşə seçimi, gələcək planlar,
    universitet və iş imkanları haqqında peşəkar və faydalı cavablar ver.
    Ona daim bu ad ilə xitab et: "{name}".
    İstifadəçi belə yazdı: "{message.text}".
    """
    await message.answer("Sualınızın cavabı hazırlanır♻️")
    response = model.generate_content(prompt)
    await message.answer(response.text)

# Main
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
    

import asyncio
import requests
from bs4 import BeautifulSoup
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from apscheduler.schedulers.asyncio import AsyncIOScheduler

TOKEN = "8702389832:AAHCGPeHaDZTp6lamaqqprIadn92aLktYbo"

URL = "https://sites.google.com/view/stcctkb/sp-k31-2025-2026?authuser=0"

bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher()
scheduler = AsyncIOScheduler()

users = {}

def get_schedule(class_name):
    try:
        r = requests.get(URL)
        soup = BeautifulSoup(r.text, "html.parser")

        text = soup.get_text("\n")

        lines = text.split("\n")

        result = []

        found = False

        for line in lines:
            if class_name.upper() in line.upper():
                found = True

            if found:
                result.append(line)

            if found and "-----" in line:
                break

        if result:
            return "\n".join(result[:20])

        return f"""
LỊCH TEST {class_name}

Thứ 2:
- Toán cao cấp
- Phòng A101
- 7h00

Thứ 3:
- Tin học
- Phòng B202
- 13h00
"""

    except Exception as e:
        return f"Lỗi: {e}"

@dp.message(Command("start"))
async def start(message: Message):
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="MN31A")],
            [KeyboardButton(text="MN31B")],
            [KeyboardButton(text="TKB hôm nay")]
        ],
        resize_keyboard=True
    )

    await message.answer(
        "Chọn lớp:",
        reply_markup=kb
    )

@dp.message(F.text.in_(["MN31A", "MN31B"]))
async def choose_class(message: Message):
    users[message.chat.id] = message.text
    await message.answer(f"Đã chọn lớp {message.text}")

@dp.message(F.text == "TKB hôm nay")
async def today(message: Message):
    class_name = users.get(message.chat.id)

    if not class_name:
        await message.answer("Hãy chọn lớp trước.")
        return

    data = get_schedule(class_name)

    await message.answer(
        f"<b>Lịch học {class_name}</b>\n\n{data}"
    )

async def send_daily():
    for chat_id, class_name in users.items():
        data = get_schedule(class_name)

        try:
            await bot.send_message(
                chat_id,
                f"📚 Lịch học ngày mai - {class_name}\n\n{data}"
            )
        except:
            pass

async def main():
    scheduler.add_job(send_daily, "cron", hour=20, minute=0)
    scheduler.start()

    print("BOT STARTED")

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

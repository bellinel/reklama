import asyncio
import os
from aiogram import Bot, Dispatcher, types
from dotenv import load_dotenv

from user_router import router
load_dotenv()

API_TOKEN = os.getenv('BOT_TOKEN')
bot = Bot(token=API_TOKEN)
dp = Dispatcher()


dp.include_router(router)

async def main():
    print("Бот запущен")
   
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

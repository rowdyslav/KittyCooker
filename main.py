from asyncio import run
from logging import INFO, basicConfig
from sys import stdout

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from beanie import init_beanie
from pymongo import AsyncMongoClient

from commands import all_commands
from deploy import keep_alive
from env import BOT_TOKEN, DB_NAME, DB_URL
from models import Recipe

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN),
)
dp = Dispatcher()


async def main() -> None:
    await init_beanie(
        database=AsyncMongoClient(DB_URL, uuidRepresentation="standard")[DB_NAME],
        document_models=[Recipe],
    )
    await bot.delete_webhook(drop_pending_updates=True)
    dp.include_routers(*all_commands)
    await dp.start_polling(bot)


if __name__ == "__main__":
    basicConfig(level=INFO, stream=stdout)
    keep_alive()
    run(main())

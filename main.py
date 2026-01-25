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
from env import BOT_TOKEN, DB_URL
from models import Recipe

keep_alive()

dp = Dispatcher()


async def main() -> None:
    dp.include_routers(*all_commands)
    await init_beanie(
        database=AsyncMongoClient(DB_URL, uuidRepresentation="standard")["KittyCooker"],
        document_models=[Recipe],
    )
    await dp.start_polling(
        Bot(
            token=BOT_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN),
        )
    )


if __name__ == "__main__":
    basicConfig(level=INFO, stream=stdout)
    run(main())

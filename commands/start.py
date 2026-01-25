from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup

router = Router()


@router.message(CommandStart())
async def start(message: Message) -> None:
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="/create"), KeyboardButton(text="/list")]],
        resize_keyboard=True,
    )

    await message.answer(
        f"Приветик, {message.from_user.username}!😋\nС помощью этого бота ты можешь придумать, что сегодня приготовить, а также добавить новые рецепты.",
        reply_markup=keyboard,
    )

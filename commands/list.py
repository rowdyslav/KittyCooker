from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from models import Recipe
from utils.formats import format_recipe_view
from utils.shared import RECIPES_PER_PAGE, Category

router = Router()


@router.message(Command("list"))
async def choose_category_handler(message: Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=cat.label,
                    callback_data=f"list_cat:{cat.value}:page:1",
                )
            ]
            for cat in Category
        ]
    )
    await message.answer("Выберите категорию:", reply_markup=keyboard)


@router.callback_query(F.data.startswith("list_cat:"))
async def recipes_by_category_callback(callback: CallbackQuery):
    try:
        _, cat_id, _, page = callback.data.split(":")
        page = int(page)
    except ValueError:
        return await callback.answer("Некорректные данные", show_alert=True)

    category = Category.from_id(cat_id)
    skip = (page - 1) * RECIPES_PER_PAGE
    limit = RECIPES_PER_PAGE

    recipes = (
        await Recipe.find(Recipe.category == category)
        .skip(skip)
        .limit(limit + 1)
        .to_list()
    )

    if not recipes:
        # Кнопка возврата к категориям, если рецептов нет
        back_keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="⬅️ К категориям",
                        callback_data="list_back_to_categories",
                    )
                ]
            ]
        )
        await callback.message.edit_text(
            f"Рецептов в категории «{category.label}» нет.",
            reply_markup=back_keyboard,
        )
        await callback.answer()
        return

    has_next = len(recipes) > limit
    recipes = recipes[:limit]

    keyboard_rows: list[list[InlineKeyboardButton]] = []
    for recipe in recipes:
        keyboard_rows.append(
            [
                InlineKeyboardButton(
                    text=recipe.name,
                    callback_data=f"list_recipe:{recipe.id}:cat:{category.value}:page:{page}",
                )
            ]
        )

    nav_buttons: list[InlineKeyboardButton] = []
    if page > 1:
        nav_buttons.append(
            InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data=f"list_cat:{category.value}:page:{page - 1}",
            )
        )
    if has_next:
        nav_buttons.append(
            InlineKeyboardButton(
                text="➡️ Далее",
                callback_data=f"list_cat:{category.value}:page:{page + 1}",
            )
        )

    if nav_buttons:
        keyboard_rows.append(nav_buttons)

    # Добавляем кнопку "К категориям" внизу
    keyboard_rows.append(
        [
            InlineKeyboardButton(
                text="📂 К категориям",
                callback_data="list_back_to_categories",
            )
        ]
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_rows)

    await callback.message.edit_text(
        f"📂 Категория: <b>{category.label}</b>\nВыберите рецепт:",
        reply_markup=keyboard,
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data.startswith("list_recipe:"))
async def recipe_view_callback(callback: CallbackQuery):
    try:
        _, recipe_id, _, cat_id, _, page = callback.data.split(":")
        page = int(page)
    except ValueError:
        return await callback.answer("Некорректные данные", show_alert=True)

    recipe = await Recipe.get(recipe_id)
    if not recipe:
        return await callback.answer("Рецепт не найден", show_alert=True)

    category = Category.from_id(cat_id)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⬅️ К списку рецептов",
                    callback_data=f"list_cat:{category.value}:page:{page}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="📂 К категориям",
                    callback_data="list_back_to_categories",
                )
            ],
        ]
    )

    await callback.message.edit_text(
        format_recipe_view(recipe),
        parse_mode="HTML",
        reply_markup=keyboard,
    )
    await callback.answer()


@router.callback_query(F.data == "list_back_to_categories")
async def back_to_categories_callback(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=cat.label,
                    callback_data=f"list_cat:{cat.value}:page:1",
                )
            ]
            for cat in Category
        ]
    )
    await callback.message.edit_text(
        "Выберите категорию:",
        reply_markup=keyboard,
    )
    await callback.answer()

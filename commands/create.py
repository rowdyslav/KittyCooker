from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from models import Ingredient, IngredientDraft, Recipe
from utils.constants import (
    FINISH_BUTTON,
    Category,
    Unit,
)
from utils.formatting import (
    format_draft,
    format_ingredients,
    format_recipe_view,
)

router = Router()


async def render_ingredient_screen(
    *,
    bot,
    chat_id: int,
    message_id: int,
    ingredients: list[dict],
    draft: dict | None,
    footer: str,
    reply_markup=None,
):
    text = (
        "🍽 Добавленные ингредиенты:\n"
        f"{format_ingredients(ingredients)}\n\n"
        "✏️ Текущий ингредиент:\n"
        f"{format_draft(draft)}\n\n"
        f"{footer}"
    )
    await bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text=text,
        reply_markup=reply_markup,
    )


category_inline_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text=c.label, callback_data=f"cat:{c.id}")]
        for c in Category
    ]
)

units_inline_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text=u.value,
                callback_data=f"unit:{u.name}",
            )
            for u in list(Unit)[i : i + 3]
        ]
        for i in range(0, len(Unit), 3)
    ]
)

finish_inline_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text=FINISH_BUTTON, callback_data="finish_ings")]
    ]
)


class CreateRecipeStates(StatesGroup):
    category = State()
    name = State()
    ing_name = State()
    ing_qty = State()
    ing_unit = State()
    text = State()


@router.message(Command("create"))
async def cmd_create(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(CreateRecipeStates.category)
    await message.answer(
        "Создаём новый рецепт.\nВыберите категорию:",
        reply_markup=category_inline_kb,
    )


@router.callback_query(CreateRecipeStates.category, F.data.startswith("cat:"))
async def category_chosen(call: CallbackQuery, state: FSMContext):
    category_id = call.data.removeprefix("cat:")
    category = Category.from_id(category_id)

    await state.update_data(
        category=category,
        ingredients=[],
        draft=None,
    )

    await state.set_state(CreateRecipeStates.name)
    await call.message.edit_text("Введите название рецепта:")
    await call.answer()


@router.message(CreateRecipeStates.name)
async def recipe_name(message: Message, state: FSMContext):
    name = message.text.strip()
    if not name:
        return await message.answer("Название не может быть пустым.")

    await state.update_data(name=name)
    await state.set_state(CreateRecipeStates.ing_name)

    msg = await message.answer("Введите название ингредиента:")
    await state.update_data(main_msg_id=msg.message_id)


@router.message(CreateRecipeStates.ing_name)
async def ing_name(message: Message, state: FSMContext):
    name = message.text.strip()
    if not name:
        return

    draft = IngredientDraft(name=name)

    data = await state.get_data()
    await state.update_data(draft=draft)
    await state.set_state(CreateRecipeStates.ing_qty)

    await message.delete()
    await render_ingredient_screen(
        bot=message.bot,
        chat_id=message.chat.id,
        message_id=data["main_msg_id"],
        ingredients=data["ingredients"],
        draft=draft.model_dump(),
        footer="Введите количество:",
    )


@router.message(CreateRecipeStates.ing_qty)
async def ing_qty(message: Message, state: FSMContext):
    try:
        qty = int(message.text)
        if qty <= 0:
            raise ValueError
    except ValueError:
        return await message.answer("Введите положительное число.")

    data = await state.get_data()
    draft: IngredientDraft = data["draft"]
    draft.quantity = qty

    await state.update_data(draft=draft)
    await state.set_state(CreateRecipeStates.ing_unit)

    await message.delete()
    await render_ingredient_screen(
        bot=message.bot,
        chat_id=message.chat.id,
        message_id=data["main_msg_id"],
        ingredients=data["ingredients"],
        draft=draft.model_dump(),
        footer="Выберите единицу измерения:",
        reply_markup=units_inline_kb,
    )


@router.callback_query(CreateRecipeStates.ing_unit, F.data.startswith("unit:"))
async def ing_unit(call: CallbackQuery, state: FSMContext):
    unit = Unit[call.data.removeprefix("unit:")]

    data = await state.get_data()
    draft: IngredientDraft = data["draft"]
    draft.unit = unit

    ingredients: list[Ingredient] = data["ingredients"]
    ingredients.append(
        Ingredient(
            name=draft.name,
            quantity=draft.quantity,
            unit=draft.unit,
        )
    )

    await state.update_data(
        ingredients=ingredients,
        draft=None,
    )
    await state.set_state(CreateRecipeStates.ing_name)

    await render_ingredient_screen(
        bot=call.bot,
        chat_id=call.message.chat.id,
        message_id=data["main_msg_id"],
        ingredients=ingredients,
        draft=None,
        footer="Введите следующий ингредиент или нажмите «Завершить».",
        reply_markup=finish_inline_kb,
    )

    await call.answer()


@router.callback_query(F.data == "finish_ings")
async def finish_ings(call: CallbackQuery, state: FSMContext):
    await state.get_data()
    await state.set_state(CreateRecipeStates.text)
    await call.message.edit_text("Введите текст рецепта (описание приготовления):")
    await call.answer()


@router.message(CreateRecipeStates.text)
async def recipe_text(message: Message, state: FSMContext):
    text = message.text.strip()
    if not text:
        return await message.answer("Текст рецепта не может быть пустым.")

    data = await state.get_data()

    recipe = Recipe(
        category=data["category"],
        name=data["name"],
        ingredients=data["ingredients"],
        text=text,
    )

    await recipe.insert()

    await message.answer(
        "Рецепт успешно создан!\n\n" + format_recipe_view(recipe),
        parse_mode="HTML",
    )
    await state.clear()

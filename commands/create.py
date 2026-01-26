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
from utils.formats import (
    format_draft,
    format_ingredients,
    format_recipe_view,
)
from utils.shared import (
    FINISH_BUTTON,
    Category,
    Unit,
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


category_ikb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text=c.label, callback_data=f"create_cat:{c.value}")]
        for c in Category
    ]
)

back_ikb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="create_back")]
    ]
)

units_ikb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text=u.value,
                callback_data=f"create_unit:{u.value}",
            )
            for u in list(Unit)[i : i + 3]
        ]
        for i in range(0, len(Unit), 3)
    ]
    + [[InlineKeyboardButton(text="⬅️ Назад", callback_data="create_back")]]
)

finish_ikb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text=FINISH_BUTTON, callback_data="create_finish_ings"
            ),
            InlineKeyboardButton(text="⬅️ Назад", callback_data="create_back_to_unit"),
        ]
    ]
)


class CreateStates(StatesGroup):
    category = State()
    name = State()
    ing_name = State()
    ing_qty = State()
    ing_unit = State()
    text = State()


@router.message(Command("create"))
async def cmd_create(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(CreateStates.category)
    await message.answer(
        "Создаём новый рецепт.\nВыберите категорию:",
        reply_markup=category_ikb,
    )


@router.callback_query(CreateStates.category, F.data.startswith("create_cat:"))
async def category_chosen(call: CallbackQuery, state: FSMContext):
    category_id = call.data.removeprefix("create_cat:")
    category = Category(category_id)

    await state.update_data(
        category=category,
        ingredients=[],
        draft=None,
        main_msg_id=call.message.message_id,
    )

    await state.set_state(CreateStates.name)
    await call.message.edit_text(
        "Введите название рецепта:",
        reply_markup=back_ikb,
    )
    await call.answer()


@router.message(CreateStates.name)
async def recipe_name(message: Message, state: FSMContext):
    name = message.text.strip()
    if not name:
        return await message.answer(
            "Название не может быть пустым.", reply_markup=back_ikb
        )

    await state.update_data(name=name)
    await state.set_state(CreateStates.ing_name)

    await message.delete()

    data = await state.get_data()
    await message.bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=data["main_msg_id"],
        text="Введите название ингредиента:",
        reply_markup=back_ikb,
    )


@router.message(CreateStates.ing_name)
async def ing_name(message: Message, state: FSMContext):
    name = message.text.strip()
    if not name:
        return

    draft = IngredientDraft(name=name)

    data = await state.get_data()
    await state.update_data(draft=draft)
    await state.set_state(CreateStates.ing_qty)

    await message.delete()
    await render_ingredient_screen(
        bot=message.bot,
        chat_id=message.chat.id,
        message_id=data["main_msg_id"],
        ingredients=data["ingredients"],
        draft=draft.model_dump(),
        footer="Введите количество:",
        reply_markup=back_ikb,
    )


@router.message(CreateStates.ing_qty)
async def ing_qty(message: Message, state: FSMContext):
    try:
        qty = int(message.text)
        if qty <= 0:
            raise ValueError
    except ValueError:
        return await message.answer(
            "Введите положительное число.", reply_markup=back_ikb
        )

    data = await state.get_data()
    draft: IngredientDraft = data["draft"]
    draft.quantity = qty

    await state.update_data(draft=draft)
    await state.set_state(CreateStates.ing_unit)

    await message.delete()
    await render_ingredient_screen(
        bot=message.bot,
        chat_id=message.chat.id,
        message_id=data["main_msg_id"],
        ingredients=data["ingredients"],
        draft=draft.model_dump(),
        footer="Выберите единицу измерения:",
        reply_markup=units_ikb,
    )


@router.callback_query(CreateStates.ing_unit, F.data.startswith("create_unit:"))
async def ing_unit(call: CallbackQuery, state: FSMContext):
    unit_value = call.data.removeprefix("create_unit:")
    unit = Unit(unit_value)

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

    # Сохраняем последний draft для возможности возврата к юнитам
    await state.update_data(
        ingredients=ingredients,
        last_draft=draft,
        draft=None,
    )
    await state.set_state(CreateStates.ing_name)

    await render_ingredient_screen(
        bot=call.bot,
        chat_id=call.message.chat.id,
        message_id=data["main_msg_id"],
        ingredients=ingredients,
        draft=None,
        footer="Введите следующий ингредиент или нажмите «Завершить».",
        reply_markup=finish_ikb,
    )

    await call.answer()


@router.callback_query(F.data == "create_finish_ings")
async def finish_ings(call: CallbackQuery, state: FSMContext):
    await state.get_data()
    await state.set_state(CreateStates.text)
    await call.message.edit_text(
        "Введите текст рецепта (описание приготовления):", reply_markup=back_ikb
    )
    await call.answer()


@router.message(CreateStates.text)
async def recipe_text(message: Message, state: FSMContext):
    text = message.text.strip()
    if not text:
        return await message.answer(
            "Текст рецепта не может быть пустым.", reply_markup=back_ikb
        )

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


# === Обработчик кнопки "Назад" ===


@router.callback_query(F.data == "create_back_to_unit")
async def back_to_unit_after_finish(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    # Восстанавливаем последний draft
    last_draft = data.get("last_draft")
    if not last_draft:
        await call.answer(
            "Нет предыдущего ингредиента для редактирования.", show_alert=True
        )
        return

    # Удаляем последний ингредиент из списка
    ingredients = list(data["ingredients"])
    if ingredients:
        ingredients.pop()

    await state.update_data(draft=last_draft, ingredients=ingredients)
    await state.set_state(CreateStates.ing_unit)
    await render_ingredient_screen(
        bot=call.bot,
        chat_id=call.message.chat.id,
        message_id=data["main_msg_id"],
        ingredients=ingredients,
        draft=last_draft.model_dump(),
        footer="Выберите единицу измерения:",
        reply_markup=units_ikb,
    )
    await call.answer()


@router.callback_query(F.data == "create_back")
async def go_back(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    current_state = await state.get_state()

    if current_state == CreateStates.name.state:
        await state.set_state(CreateStates.category)
        await call.message.edit_text(
            "Создаём новый рецепт.\nВыберите категорию:",
            reply_markup=category_ikb,
        )
    elif current_state == CreateStates.ing_name.state:
        await state.set_state(CreateStates.name)
        await call.message.edit_text(
            "Введите название рецепта:",
            reply_markup=back_ikb,
        )
    elif current_state == CreateStates.ing_qty.state:
        # Назад к названию ингредиента
        await state.set_state(CreateStates.ing_name)
        await call.message.edit_text(
            "Введите название ингредиента:", reply_markup=back_ikb
        )
    elif current_state == CreateStates.ing_unit.state:
        # Назад к количеству ингредиента
        await state.set_state(CreateStates.ing_qty)
        await render_ingredient_screen(
            bot=call.bot,
            chat_id=call.message.chat.id,
            message_id=data["main_msg_id"],
            ingredients=data["ingredients"],
            draft=data["draft"].model_dump() if data.get("draft") else None,
            footer="Введите количество:",
            reply_markup=back_ikb,
        )
    elif current_state == CreateStates.text.state:
        # Назад к добавлению ингредиентов
        await state.set_state(CreateStates.ing_name)
        await render_ingredient_screen(
            bot=call.bot,
            chat_id=call.message.chat.id,
            message_id=data["main_msg_id"],
            ingredients=data["ingredients"],
            draft=None,
            footer="Введите следующий ингредиент или нажмите «Завершить».",
            reply_markup=finish_ikb,
        )
    await call.answer()

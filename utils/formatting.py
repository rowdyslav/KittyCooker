from typing import Optional, Sequence

from models import Ingredient, IngredientDraft, Recipe
from utils.constants import Category


def format_ingredients(ingredients: Sequence[Ingredient]) -> str:
    if not ingredients:
        return "— пока не добавлено"

    lines: list[str] = []

    for idx, ing in enumerate(ingredients, start=1):
        name = getattr(ing, "name", "—")
        quantity = getattr(ing, "quantity", None)
        unit = getattr(ing, "unit", None)

        if quantity is not None and unit:
            unit_str = unit.value if hasattr(unit, "value") else str(unit)
            lines.append(f"{idx}. {name} — {quantity} {unit_str}")
        else:
            lines.append(f"{idx}. {name}")

    return "\n".join(lines)


def format_draft(draft: Optional[IngredientDraft]) -> str:
    if not draft:
        return "—"

    parts: list[str] = []

    # Универсальный доступ к полям draft (dict или объект)
    def get(field, default=None):
        if isinstance(draft, dict):
            return draft.get(field, default)
        return getattr(draft, field, default)

    name = get("name")
    if name:
        parts.append(f"название: {name}")
    else:
        parts.append("название: —")

    quantity = get("quantity")
    if quantity is not None:
        parts.append(f"кол-во: {quantity}")

    unit = get("unit")
    if unit:
        unit_str = unit.value if hasattr(unit, "value") else str(unit)
        parts.append(f"ед.: {unit_str}")

    return ", ".join(parts)


def format_recipe_view(recipe: Recipe) -> str:
    ingredients_text = (
        "\n".join(
            f"{i + 1}. {ing.name} — {ing.quantity} {(ing.unit.value if hasattr(ing.unit, 'value') else ing.unit)}"
            for i, ing in enumerate(recipe.ingredients)
        )
        if recipe.ingredients
        else "—"
    )

    category_label = (
        recipe.category.label
        if isinstance(recipe.category, Category)
        else str(recipe.category)
    )

    return (
        f"🍽 <b>{recipe.name}</b>\n"
        f"Категория: {category_label}\n\n"
        f"<b>Ингредиенты:</b>\n"
        f"{ingredients_text}\n\n"
        f"<b>Описание:</b>\n"
        f"{recipe.text or '—'}\n\n"
        f"Готово! Приятного аппетита!😍"
    )

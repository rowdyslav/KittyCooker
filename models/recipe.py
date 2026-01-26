from beanie import Document

from utils.shared import Category

from .ingredient import Ingredient


class Recipe(Document):
    category: Category
    name: str
    ingredients: list[Ingredient]
    text: str

    class Settings:
        name = "recipes"

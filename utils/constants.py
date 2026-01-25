from enum import Enum
from typing import Final


class Category(str, Enum):
    BREAKFAST = "breakfast"
    MAIN = "main"
    DESSERT = "dessert"

    @property
    def label(self) -> str:
        return {
            "breakfast": "Завтрак🥞",
            "main": "Обед/Ужин🍝",
            "dessert": "Десерты🧁",
        }[self.value]

    @classmethod
    def from_id(cls, id_: str) -> "Category":
        return cls(id_)


class Unit(Enum):
    PCS = "шт"
    TBSP = "ст.л"
    TSP = "ч.л"
    G = "г"
    L = "л"
    ML = "мл"


FINISH_BUTTON: Final[str] = "Завершить"
ADD_MORE_BUTTON: Final[str] = "Добавить ещё"
RECIPES_PER_PAGE: Final[int] = 10

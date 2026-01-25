from enum import Enum
from typing import Final


class Category(Enum):
    BREAKFAST = ("breakfast", "Завтрак🥞")
    MAIN = ("main", "Обед/Ужин🍝")
    DESSERT = ("dessert", "Десерты🧁")

    def __init__(self, id_: str, label: str):
        self.id: Final[str] = id_
        self.label: Final[str] = label

    @classmethod
    def from_id(cls, id_: str) -> "Category":
        for c in cls:
            if c.id == id_:
                return c
        raise ValueError(f"Unknown category id: {id_}")


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

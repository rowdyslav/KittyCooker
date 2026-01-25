from pydantic import BaseModel

from utils.constants import Unit


class Ingredient(BaseModel):
    name: str
    quantity: int
    unit: Unit

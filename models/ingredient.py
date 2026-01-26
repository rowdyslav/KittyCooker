from pydantic import BaseModel

from utils.shared import Unit


class Ingredient(BaseModel):
    name: str
    quantity: int
    unit: Unit

from pydantic import BaseModel

from utils.constants import Unit


class IngredientDraft(BaseModel):
    name: str
    quantity: int | None = None
    unit: Unit | None = None

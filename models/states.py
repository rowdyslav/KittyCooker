from pydantic import BaseModel

from utils.shared import Unit


class IngredientDraft(BaseModel):
    name: str
    quantity: int | None = None
    unit: Unit | None = None

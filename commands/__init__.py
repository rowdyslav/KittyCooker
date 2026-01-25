from .create import router as create_router
from .list import router as list_router
from .start import router as start_router

all_commands = [start_router, create_router, list_router]

__all___ = ["all_commands"]

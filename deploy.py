from threading import Thread

from fastapi import FastAPI
from uvicorn import run

app = FastAPI()


@app.get("/")
async def index():
    return {}


def start_server():
    run(app, host="0.0.0.0", port=8000)


def keep_alive():
    Thread(target=start_server).start()

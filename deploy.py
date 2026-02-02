from threading import Thread

from aiohttp import ClientSession
from fastapi import FastAPI
from uvicorn import run

from env import DEPLOY_URL

app = FastAPI()


@app.get("/")
async def index():
    return {}


def start_server():
    run(app, host="0.0.0.0", port=8000)


def keep_alive():
    Thread(target=start_server).start()


async def try_revive():
    async with ClientSession() as session:
        await session.get(DEPLOY_URL)

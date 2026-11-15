"""Four endpoints: one healthy, one that blocks the loop, two that handle blocking correctly."""

import asyncio
import time

from fastapi import FastAPI

app = FastAPI()

DELAY = 2.0


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/good")
async def good() -> dict[str, float]:
    await asyncio.sleep(DELAY)  # yields to the loop; timer + epoll_wait
    return {"waited": DELAY}


@app.get("/bad")
async def bad() -> dict[str, float]:
    time.sleep(DELAY)  # noqa: ASYNC251  (deliberate, for the experiment)
    return {"waited": DELAY}


@app.get("/offloaded")
async def offloaded() -> dict[str, float]:
    await asyncio.to_thread(time.sleep, DELAY)  # worker thread; loop stays free
    return {"waited": DELAY}

"""Fire N slow requests, then measure how long /health takes while they are in flight."""

import asyncio
import sys
import time

import httpx

BASE = "http://127.0.0.1:8000"


async def timed_get(client: httpx.AsyncClient, path: str) -> float:
    start = time.perf_counter()
    await client.get(f"{BASE}{path}", timeout=60)
    return time.perf_counter() - start


async def main(path: str, n: int) -> None:
    async with httpx.AsyncClient() as client:
        slow = [asyncio.create_task(timed_get(client, path)) for _ in range(n)]
        await asyncio.sleep(0.2)  # let the slow requests reach the server first
        health = await timed_get(client, "/health")
        slowest = max(await asyncio.gather(*slow))
        print(
            f"{path:<11} n={n:<3} /health took {health * 1000:7.0f} ms   "
            f"slowest {path} took {slowest:5.2f} s"
        )


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1], int(sys.argv[2])))

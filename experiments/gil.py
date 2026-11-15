"""Measure how the GIL affects CPU-bound vs I/O-bound work."""

import os
import sys
import time
from collections.abc import Callable
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

WORKERS = 4
CPU_N = 15_000_000
IO_SECONDS = 1.0


def cpu_work(n: int) -> int:
    total = 0
    for i in range(n):
        total += i * i
    return total


def io_work(seconds: float) -> None:
    time.sleep(seconds)  # blocks in the kernel; the GIL is released while waiting


def timed(label: str, fn: Callable[[], object]) -> float:
    start = time.perf_counter()
    fn()
    elapsed = time.perf_counter() - start
    print(f"{label:<28} {elapsed:6.2f}s")
    return elapsed


def run_serial(fn: Callable[[float], object], arg: float) -> None:
    for _ in range(WORKERS):
        fn(arg)


def run_threads(fn: Callable[[float], object], arg: float) -> None:
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        list(pool.map(fn, [arg] * WORKERS))


def run_processes(fn: Callable[[float], object], arg: float) -> None:
    with ProcessPoolExecutor(max_workers=WORKERS) as pool:
        list(pool.map(fn, [arg] * WORKERS))


def cpu_wrapper(n: float) -> int:  # module-level so it can be pickled for processes
    return cpu_work(int(n))


def io_wrapper(seconds: float) -> None:
    io_work(seconds)


def main() -> None:
    print(
        f"Python {sys.version.split()[0]}, cores={os.cpu_count()}, "
        f"switch interval={sys.getswitchinterval() * 1000:.0f} ms"
    )
    gil_enabled = getattr(sys, "_is_gil_enabled", lambda: True)()
    print(f"GIL enabled: {gil_enabled}\n")

    print("CPU-bound (4 tasks)")
    timed("serial", lambda: run_serial(cpu_wrapper, CPU_N))
    timed("4 threads", lambda: run_threads(cpu_wrapper, CPU_N))
    timed("4 processes", lambda: run_processes(cpu_wrapper, CPU_N))

    print("\nI/O-bound (4 tasks, 1 s wait each)")
    timed("serial", lambda: run_serial(io_wrapper, IO_SECONDS))
    timed("4 threads", lambda: run_threads(io_wrapper, IO_SECONDS))


if __name__ == "__main__":  # required: macOS starts processes by spawning fresh interpreters
    main()
"""A single-threaded echo server on a raw readiness selector (epoll on Linux, kqueue on macOS)."""

import selectors
import socket
from collections.abc import Callable
from typing import cast

sel = selectors.DefaultSelector()
Handler = Callable[[socket.socket], None]


def accept(server: socket.socket) -> None:
    conn, _addr = server.accept()
    conn.setblocking(False)
    sel.register(conn, selectors.EVENT_READ, read)


def read(conn: socket.socket) -> None:
    data = conn.recv(1024)  # will not block: the selector said it is ready
    if data:
        conn.sendall(data)
    else:
        sel.unregister(conn)
        conn.close()


def main() -> None:
    server = socket.socket()
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("127.0.0.1", 9000))
    server.listen()
    server.setblocking(False)
    sel.register(server, selectors.EVENT_READ, accept)
    print(f"selector in use: {type(sel).__name__}  (listening on 127.0.0.1:9000)")
    while True:
        for key, _mask in sel.select():  # the thread sleeps here until something is ready
            handler = cast(Handler, key.data)
            handler(cast(socket.socket, key.fileobj))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Server local cho Agent Control Center.

Mỗi lần tải trang, server quét lại ~/.config/opencode và trả dữ liệu mới,
không cần chạy build.py. Chỉ nghe trên 127.0.0.1.

Chạy: python3 serve.py [--port 8765] [--no-open]
"""
from __future__ import annotations

import argparse
import json
import socket
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from build import build

ROOT = Path(__file__).resolve().parent
DEFAULT_PORT = 8765


class Handler(BaseHTTPRequestHandler):
    server_version = "AgentControlCenter/1.0"

    def _send(self, body: bytes, content_type: str, status: int = 200) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store, max-age=0")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802 (http.server API)
        path = self.path.split("?", 1)[0]

        if path in ("/", "/index.html"):
            self._send((ROOT / "index.html").read_bytes(), "text/html; charset=utf-8")
            return

        if path == "/data.js":
            try:
                data = build()
            except Exception as exc:  # báo lỗi rõ thay vì treo trang
                payload = (
                    "/* lỗi khi quét cấu hình */\n"
                    "window.AGENT_DATA_ERROR = " + json.dumps(str(exc)) + ";\n"
                )
                self._send(payload.encode("utf-8"), "application/javascript; charset=utf-8", 500)
                return

            payload = (
                "/* Sinh live bởi serve.py tại mỗi lần tải trang. */\n"
                "window.AGENT_DATA = " + json.dumps(data, ensure_ascii=False, indent=1) + ";\n"
            )
            self._send(payload.encode("utf-8"), "application/javascript; charset=utf-8")
            return

        if path == "/favicon.ico":
            self._send(b"", "image/x-icon", 204)
            return

        self._send(b"Not found", "text/plain; charset=utf-8", 404)

    def log_message(self, fmt: str, *args) -> None:
        # Gọn: chỉ log lỗi, không log từng request.
        if args and str(args[0]).startswith(("4", "5")):
            super().log_message(fmt, *args)


def port_available(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind(("127.0.0.1", port))
        except OSError:
            return False
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Agent Control Center local server")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--no-open", action="store_true", help="không tự mở trình duyệt")
    args = parser.parse_args()

    url = f"http://127.0.0.1:{args.port}/"

    if not port_available(args.port):
        # Server đã chạy: chỉ mở tab mới.
        print(f"Đã có server tại {url}")
        if not args.no_open:
            webbrowser.open(url)
        return

    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"Agent Control Center: {url} (Ctrl+C để dừng)")

    if not args.no_open:
        threading.Timer(0.5, webbrowser.open, args=(url,)).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nĐã dừng.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()

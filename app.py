#!/usr/bin/env python3
"""
Interactive 3D ASCII Lily Bouquet & Birthday Letter Gift Experience.
Complete experience generated and served with Python standard library.
Zero third-party dependencies required.
"""

import http.server
import os
import socket
import sys
import threading
import webbrowser
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
HTML_FILE = BASE_DIR / "index.html"


class BirthdayGiftHTTPHandler(http.server.SimpleHTTPRequestHandler):
    """Custom HTTP handler serving the complete interactive birthday gift experience."""

    extensions_map = {
        **http.server.SimpleHTTPRequestHandler.extensions_map,
        ".html": "text/html; charset=utf-8",
        ".css": "text/css; charset=utf-8",
        ".js": "application/javascript; charset=utf-8",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(BASE_DIR), **kwargs)

    def do_GET(self):
        # Serve index.html for root requests
        if self.path in ("/", ""):
            self.path = "/index.html"
        return super().do_GET()

    def end_headers(self):
        # Prevent caching so edits appear immediately
        self.send_header("Cache-Control", "no-store, must-revalidate")
        super().end_headers()

    def log_message(self, format_str, *args):
        # Clean logging
        status = args[1] if len(args) > 1 else ""
        if str(status).startswith(("4", "5")):
            super().log_message(format_str, *args)


def find_free_port(host: str = "127.0.0.1", start_port: int = 8000, max_tries: int = 25) -> int:
    """Finds an available local port starting from start_port."""
    for port in range(start_port, start_port + max_tries):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                sock.bind((host, port))
                return port
            except OSError:
                continue
    return start_port


def main():
    host = "127.0.0.1"
    port = find_free_port(host, 8000)
    url = f"http://localhost:{port}/"

    print("=" * 64)
    print("💐  INTERACTIVE 3D ASCII LILY BOUQUET & BIRTHDAY LETTER  💐")
    print(f"✨  Serving locally at: {url}")
    print("💌  Press Ctrl+C in the terminal anytime to stop the server.")
    print("=" * 64)

    # Launch browser automatically
    def open_browser():
        try:
            webbrowser.open(url)
        except Exception:
            pass

    threading.Timer(0.8, open_browser).start()

    server_address = (host, port)
    httpd = http.server.ThreadingHTTPServer(server_address, BirthdayGiftHTTPHandler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🌸 Birthday server stopped gracefully. Have a lovely day!")
        sys.exit(0)


if __name__ == "__main__":
    main()

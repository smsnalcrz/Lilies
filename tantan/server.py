#!/usr/bin/env python3
"""
Local web server for the Interactive 3D ASCII Lily Bouquet birthday gift.
Uses only Python's built-in standard library (no external packages required).
"""

import argparse
import functools
import http.server
import os
import socket
import sys
import threading
import webbrowser


class QuietHTMLHandler(http.server.SimpleHTTPRequestHandler):
    """Serves static files with UTF-8 headers and clean console logging."""

    extensions_map = {
        **http.server.SimpleHTTPRequestHandler.extensions_map,
        ".html": "text/html; charset=utf-8",
        ".css": "text/css; charset=utf-8",
        ".js": "application/javascript; charset=utf-8",
    }

    def end_headers(self):
        # Prevent aggressive browser caching while customizing the letter or colors
        self.send_header("Cache-Control", "no-store, must-revalidate")
        super().end_headers()

    def log_message(self, format_str, *args):
        # Keep terminal output tidy and friendly
        status = args[1] if len(args) > 1 else ""
        if str(status).startswith(("4", "5")):
            super().log_message(format_str, *args)


class ReusableThreadingHTTPServer(http.server.ThreadingHTTPServer):
    allow_reuse_address = True
    daemon_threads = True


def find_available_port(host: str, preferred_port: int, max_tries: int = 15) -> int:
    """Return preferred_port if free, otherwise scan upward for an open port."""
    for port in range(preferred_port, preferred_port + max_tries):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                sock.bind((host, port))
                return port
            except OSError:
                continue
    raise OSError(f"No open ports found in range {preferred_port}-{preferred_port + max_tries - 1}.")


def main():
    parser = argparse.ArgumentParser(description="Serve the 3D ASCII Lily Bouquet birthday gift.")
    parser.add_argument("--host", default="127.0.0.1", help="Host address to bind (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="Preferred port number (default: 8000)")
    parser.add_argument("--no-browser", action="store_true", help="Do not automatically open the browser")
    args = parser.parse_args()

    # Always serve from the folder containing server.py
    base_dir = os.path.dirname(os.path.abspath(__file__))
    index_path = os.path.join(base_dir, "index.html")
    if not os.path.isfile(index_path):
        print(f"Error: Could not find index.html in {base_dir}")
        sys.exit(1)

    port = find_available_port(args.host, args.port)
    url = f"http://localhost:{port}" if args.host in ("127.0.0.1", "localhost") else f"http://{args.host}:{port}"

    handler = functools.partial(QuietHTMLHandler, directory=base_dir)
    server = ReusableThreadingHTTPServer((args.host, port), handler)

    print("=" * 56)
    print("  3D ASCII Lily Bouquet — Birthday Gift Server")
    print("=" * 56)
    print(f"  Serving from : {base_dir}")
    print(f"  Open in browser: {url}")
    print("  Press Ctrl+C to stop the server.")
    print("=" * 56)

    if not args.no_browser:
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped gracefully. Happy Birthday!")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
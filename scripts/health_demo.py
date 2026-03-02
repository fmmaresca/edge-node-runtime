#!/usr/bin/env python3
from http.server import BaseHTTPRequestHandler, HTTPServer
import os

HOST = os.getenv("HEALTH_HOST", "127.0.0.1")
PORT = int(os.getenv("HEALTH_PORT", "8081"))

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            fail = os.getenv("HEALTH_FAIL", "0") == "1"
            code = 500 if fail else 200
            body = b"FAIL\n" if fail else b"OK\n"
            self.send_response(code)
            self.send_header("Content-Type", "text/plain")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        self.send_response(404)
        self.end_headers()

    def log_message(self, fmt, *args):
        # keep stdout clean (optional)
        return

def main():
    httpd = HTTPServer((HOST, PORT), Handler)
    print(f"health_demo listening on http://{HOST}:{PORT}/health", flush=True)
    httpd.serve_forever()

if __name__ == "__main__":
    main()

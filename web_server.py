"""
ConnectX Telecom Customer Support Web Server
Provides a web portal interface for customers to view their account
and interact with the ConnectX Customer Support Assistant.
Run:
    python web_server.py
Then open http://localhost:8000 in your browser.
"""
import http.server
import json
import os
import sys
from urllib.parse import urlparse

# Ensure UTF-8 output encoding on Windows consoles
if sys.platform == "win32":
    try:
        if sys.stdout and hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
        if sys.stderr and hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from chatbot import SupportBot, ACCOUNT, PLANS, BACKEND, MAIN_MODEL, ROUTER_MODEL

PORT = int(os.getenv("PORT", 8000))
bot = SupportBot()


class ConnectXHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/account":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            data = {"account": ACCOUNT, "plans": PLANS}
            self.wfile.write(json.dumps(data).encode("utf-8"))
            return

        if parsed.path == "/api/status":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            data = {
                "backend": BACKEND,
                "model": MAIN_MODEL,
                "router": ROUTER_MODEL,
                "history_length": len(bot.history),
                "has_summary": bool(bot.summary),
            }
            self.wfile.write(json.dumps(data).encode("utf-8"))
            return

        if parsed.path in ("/", "/index.html"):
            index_path = os.path.join(os.path.dirname(__file__), "web", "index.html")
            if os.path.exists(index_path):
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                with open(index_path, "rb") as f:
                    self.wfile.write(f.read())
                return

        return super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        content_len = int(self.headers.get("Content-Length", 0))
        post_body = self.rfile.read(content_len).decode("utf-8") if content_len > 0 else "{}"

        try:
            payload = json.loads(post_body)
        except Exception:
            payload = {}

        if parsed.path == "/api/reset":
            bot.reset()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok", "message": "Memory reset successfully"}).encode("utf-8"))
            return

        if parsed.path == "/api/chat":
            user_msg = payload.get("message", "").strip()
            if not user_msg:
                self.send_response(400)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Empty message"}).encode("utf-8"))
                return

            # Check router classification tag for observability in the UI
            classification = bot._classify(user_msg) if bot.use_router else "IN_SCOPE"
            reply = bot.chat(user_msg)

            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            res = {
                "response": reply,
                "classification": classification,
                "history_length": len(bot.history),
                "summary": bot.summary,
            }
            self.wfile.write(json.dumps(res).encode("utf-8"))
            return

        self.send_response(404)
        self.end_headers()


def run():
    server_address = ("", PORT)
    httpd = http.server.ThreadingHTTPServer(server_address, ConnectXHandler)
    print(f"ConnectX Support Server running on http://localhost:{PORT}")
    print(f"Backend: {BACKEND} | Model: {MAIN_MODEL}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")


if __name__ == "__main__":
    run()

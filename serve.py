"""Play The Last Day Inn in a browser.

    python3 serve.py            # then open http://localhost:8000
    python3 serve.py --port 8080

A small local server: it serves web/ and passes clicks to the same engine the terminal and the
playtest agent use. One game at a time (this is a local playtest build, not a public demo).
"""

import json
import os
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

from engine import Game

ROOT = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.join(ROOT, "web")
game = None


def snapshot(turn=None):
    return {"state": game.state(), "turn": turn}


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB, **kwargs)

    def log_message(self, *args):  # keep the terminal quiet; sessions are logged in logs/
        pass

    def send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/api/world":  # labels, names and layout the page needs before a game starts
            w = Game().w
            with open(os.path.join(WEB, "layout.json"), encoding="utf-8") as f:
                layout = json.load(f)
            return self.send_json({"title": w["meta"]["title"], "ui": w["ui"], "layout": layout,
                                   "phases": w["time"]["phases"]})
        if self.path == "/api/state":
            return self.send_json(snapshot() if game else {"state": None})
        return super().do_GET()

    def do_POST(self):
        global game
        length = int(self.headers.get("Content-Length") or 0)
        data = json.loads(self.rfile.read(length) or b"{}")
        if self.path == "/api/new":
            game = Game(journal=bool(data.get("journal", True)), log_dir=os.path.join(ROOT, "logs"))
            return self.send_json(snapshot())
        if game is None:
            return self.send_json({"error": "No game yet."}, 400)
        if self.path == "/api/act":
            try:
                game.act(data.get("action", ""))
            except ValueError as e:
                return self.send_json({"error": str(e)}, 400)
            return self.send_json(snapshot(game.last_turn))
        if self.path == "/api/answer":
            game.answer_end_prompt(str(data.get("answer", "")).strip())
            return self.send_json({"ok": True})
        return self.send_json({"error": "Unknown request."}, 404)


def main():
    port = int(sys.argv[sys.argv.index("--port") + 1]) if "--port" in sys.argv else 8000
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print("The Last Day Inn: open http://localhost:%d (Ctrl+C to stop)" % port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nGoodbye.")


if __name__ == "__main__":
    main()

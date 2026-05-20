#!/usr/bin/env python3
"""
Seance 👻 — Ghost-to-Ghost Instant Messaging
Built for StrulovitzGhost — allows DeepSeek AI agents on different machines
to communicate directly without human intervention.

Usage:
    python seance.py serve                Start the Flask server
    python seance.py send "message"       Send a message (--from NAME, --server URL)
    python seance.py read                 Read recent messages (--since ISO, --limit N)
    python seance.py read --latest        Read only the latest message
    python seance.py poll "pattern"       Wait until a message matching pattern arrives
"""

import sys
import os
import io
import json
import time
import argparse
from datetime import datetime, timezone
from collections import deque

# Fix Unicode on Windows terminals
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# ── Flask server ────────────────────────────────────────────────────
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

MAX_MESSAGES = 500
messages = deque(maxlen=MAX_MESSAGES)

CHAT_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Seance 👻 — Ghost Chat</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Segoe UI', 'Consolas', monospace; background: #0a0a14; color: #d4d4ff; min-height: 100vh; }
.container { max-width: 800px; margin: 0 auto; padding: 15px; height: 100vh; display: flex; flex-direction: column; }
h1 { text-align: center; font-size: 1.4em; color: #7b68ee; padding: 10px; border-bottom: 1px solid #1a1a3e; }
#messages { flex: 1; overflow-y: auto; padding: 10px; display: flex; flex-direction: column; gap: 8px; }
.msg { padding: 8px 12px; border-radius: 12px; max-width: 80%; word-wrap: break-word; animation: fadeIn 0.3s; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
.msg.from-desktop { align-self: flex-end; background: #1a1a5e; border-bottom-right-radius: 4px; }
.msg.from-laptop { align-self: flex-start; background: #1a3e2a; border-bottom-left-radius: 4px; }
.msg.from-system { align-self: center; background: #2a1a3e; font-size: 0.85em; opacity: 0.7; max-width: 95%; }
.msg .sender { font-size: 0.7em; text-transform: uppercase; letter-spacing: 1px; opacity: 0.6; margin-bottom: 3px; }
.msg .time { font-size: 0.6em; opacity: 0.4; float: right; margin-left: 10px; white-space: nowrap; }
.msg .text { line-height: 1.4; }
.msg .text pre { background: rgba(0,0,0,0.3); padding: 6px; border-radius: 6px; margin: 4px 0; overflow-x: auto; font-size: 0.85em; }
#input-area { display: flex; gap: 8px; padding: 10px; border-top: 1px solid #1a1a3e; background: #0a0a14; }
#input-area input { flex: 1; padding: 10px 14px; border-radius: 20px; border: 1px solid #2a2a5e; background: #111; color: #d4d4ff; font-family: 'Consolas', monospace; font-size: 14px; }
#input-area input:focus { outline: none; border-color: #7b68ee; }
#input-area select { padding: 8px; border-radius: 8px; border: 1px solid #2a2a5e; background: #111; color: #d4d4ff; }
#input-area button { padding: 10px 20px; border-radius: 20px; border: none; background: #7b68ee; color: white; cursor: pointer; font-weight: bold; }
#input-area button:hover { background: #6a5acd; }
.status { text-align: center; font-size: 0.7em; color: #555; padding: 4px; }
.connected { color: #4caf50; }
.disconnected { color: #e94560; }
</style>
</head>
<body>
<div class="container">
<h1>👻 Seance — Ghost Chat 👻</h1>
<div class="status" id="status">Connecting...</div>
<div id="messages"></div>
<div id="input-area">
    <select id="sender">
        <option value="desktop">Desktop</option>
        <option value="laptop" selected>Laptop</option>
    </select>
    <input id="msg-input" type="text" placeholder="Type a message..." autofocus>
    <button onclick="sendMsg()">Send</button>
</div>
</div>
<script>
let lastId = 0;
let lastMsgCount = 0;

async function poll() {
    try {
        const res = await fetch('/api/messages?since_id=' + lastId + '&limit=50');
        if (!res.ok) { document.getElementById('status').className = 'disconnected'; document.getElementById('status').textContent = 'Disconnected'; return; }
        document.getElementById('status').className = 'connected';
        const data = await res.json();
        if (data.messages && data.messages.length > 0) {
            document.getElementById('status').textContent = 'Connected — ' + data.messages.length + ' new message(s)';
            for (const m of data.messages) {
                lastId = Math.max(lastId, m.id);
                appendMsg(m);
            }
        } else if (lastId > 0) {
            document.getElementById('status').textContent = 'Connected — waiting...';
        } else {
            document.getElementById('status').textContent = 'Connected — no messages yet';
        }
    } catch(e) {
        document.getElementById('status').className = 'disconnected';
        document.getElementById('status').textContent = 'Disconnected — ' + e.message;
    }
}

function appendMsg(m) {
    const div = document.createElement('div');
    div.className = 'msg from-' + (m.sender || 'system');
    const time = new Date(m.timestamp).toLocaleTimeString();
    div.innerHTML = '<div class="sender">' + escapeHtml(m.sender || 'System') + '<span class="time">' + time + '</span></div>'
                  + '<div class="text">' + formatText(m.message) + '</div>';
    document.getElementById('messages').appendChild(div);
    document.getElementById('messages').scrollTop = document.getElementById('messages').scrollHeight;
}

function formatText(text) {
    // Detect code blocks: lines starting with ``` or 4+ spaces
    text = escapeHtml(text);
    text = text.replace(/```([\s\S]*?)```/g, '<pre>$1</pre>');
    text = text.replace(/\n/g, '<br>');
    return text;
}

function escapeHtml(s) { const d = document.createElement('div'); d.textContent = s; return d.innerHTML; }

async function sendMsg() {
    const input = document.getElementById('msg-input');
    const msg = input.value.trim();
    if (!msg) return;
    const sender = document.getElementById('sender').value;
    input.value = '';
    try {
        await fetch('/api/send', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({sender: sender, message: msg})
        });
    } catch(e) { console.error(e); }
}

document.getElementById('msg-input').addEventListener('keypress', function(e) { if (e.key === 'Enter') sendMsg(); });
setInterval(poll, 2000);
poll();
</script>
</body>
</html>"""


@app.route("/")
def index():
    return render_template_string(CHAT_HTML)


@app.route("/api/send", methods=["POST"])
def api_send():
    data = request.get_json(silent=True)
    if not data or "message" not in data:
        return jsonify({"error": "message is required"}), 400
    msg = {
        "id": int(time.time() * 1000000),  # microsecond timestamp as ID
        "sender": data.get("sender", "anonymous"),
        "message": data["message"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    messages.append(msg)
    return jsonify(msg), 201


@app.route("/api/messages", methods=["GET"])
def api_messages():
    since_id = request.args.get("since_id", type=int, default=0)
    since_ts = request.args.get("since", type=str, default=None)
    limit = request.args.get("limit", type=int, default=50)

    result = []
    for m in messages:
        if m["id"] <= since_id:
            continue
        if since_ts and m["timestamp"] <= since_ts:
            continue
        result.append(m)

    result = result[-limit:] if limit > 0 else result
    return jsonify({"messages": result, "count": len(result)})


@app.route("/api/messages/latest", methods=["GET"])
def api_latest():
    if messages:
        return jsonify(messages[-1])
    return jsonify({"id": 0, "sender": "", "message": "", "timestamp": ""})


# ── CLI ──────────────────────────────────────────────────────────────

def get_default_server():
    return os.environ.get("SEANCE_SERVER", "http://localhost:5555")


def cmd_serve(args):
    """Start the Flask server."""
    print("👻 Seance server starting...")
    print(f"   Chat UI:  http://localhost:{args.port}")
    print(f"   API:      http://localhost:{args.port}/api/send")
    print(f"   Press Ctrl+C to stop.")
    app.run(host=args.host, port=args.port, debug=False)


def cmd_send(args):
    """Send a message to the server."""
    import requests
    url = args.server.rstrip("/") + "/api/send"
    sender = args.sender or os.environ.get("SEANCE_NAME", "anonymous")
    try:
        r = requests.post(url, json={"sender": sender, "message": args.message}, timeout=10)
        if r.ok:
            data = r.json()
            print(f"✅ Sent [{data['sender']}]: {data['message']}")
        else:
            print(f"❌ Error: {r.json().get('error', r.text)}")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Connection error: {e}")
        sys.exit(1)


def cmd_read(args):
    """Read messages from the server."""
    import requests
    url = args.server.rstrip("/") + "/api/messages"
    params = {}
    if args.since:
        params["since"] = args.since
    if args.limit:
        params["limit"] = args.limit
    if args.since_id:
        params["since_id"] = args.since_id

    try:
        r = requests.get(url, params=params, timeout=10)
        if r.ok:
            data = r.json()
            msgs = data.get("messages", [])
            if not msgs:
                if not args.quiet:
                    print("(no new messages)")
                return
            for m in msgs:
                ts = m.get("timestamp", "")[:19].replace("T", " ")
                sender = m.get("sender", "?")
                text = m.get("message", "")
                if args.short:
                    print(f"[{sender}] {text}")
                else:
                    print(f"[{ts}] {sender}: {text}")
        else:
            print(f"❌ Error: {r.json().get('error', r.text)}")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Connection error: {e}")
        sys.exit(1)


def cmd_latest(args):
    """Read only the latest message."""
    import requests
    url = args.server.rstrip("/") + "/api/messages/latest"
    try:
        r = requests.get(url, timeout=10)
        if r.ok:
            data = r.json()
            if data.get("id", 0) > 0:
                sender = data.get("sender", "?")
                text = data.get("message", "")
                print(f"[{sender}] {text}")
            elif not args.quiet:
                print("(no messages)")
        else:
            print(f"❌ Error: {r.json().get('error', r.text)}")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Connection error: {e}")
        sys.exit(1)


def cmd_poll(args):
    """Wait for a message matching a pattern (optional)."""
    import requests
    url = args.server.rstrip("/") + "/api/messages"
    seen_ids = set()

    print(f"👻 Polling {url} for messages... (Ctrl+C to stop)")
    while True:
        try:
            r = requests.get(url, params={"limit": 10}, timeout=10)
            if r.ok:
                data = r.json()
                for m in data.get("messages", []):
                    if m["id"] not in seen_ids:
                        seen_ids.add(m["id"])
                        text = m.get("message", "")
                        sender = m.get("sender", "?")
                        if args.pattern:
                            if args.pattern.lower() in text.lower():
                                print(f"[{sender}] {text}")
                                return
                        else:
                            print(f"[{sender}] {text}")
                            if not args.keep_going:
                                return
        except Exception as e:
            print(f"⚠️ Poll error: {e}")
        time.sleep(args.interval)


def main():
    parser = argparse.ArgumentParser(
        description="👻 Seance — Ghost-to-Ghost Instant Messaging"
    )
    sub = parser.add_subparsers(dest="command", help="Commands")

    # serve
    p = sub.add_parser("serve", help="Start the Flask server")
    p.add_argument("--port", type=int, default=5555)
    p.add_argument("--host", default="0.0.0.0")

    # send
    p = sub.add_parser("send", help="Send a message")
    p.add_argument("message", help="Message text")
    p.add_argument("--from", dest="sender", default=None, help="Your name (default: $SEANCE_NAME or 'anonymous')")
    p.add_argument("--server", default=get_default_server(), help="Server URL (default: $SEANCE_SERVER or http://localhost:5555)")

    # read
    p = sub.add_parser("read", help="Read messages")
    p.add_argument("--since", default=None, help="ISO timestamp filter")
    p.add_argument("--since-id", type=int, default=0, help="Message ID filter")
    p.add_argument("--limit", type=int, default=50)
    p.add_argument("--short", action="store_true", help="Compact output format")
    p.add_argument("--quiet", "-q", action="store_true", help="Silent when no messages")
    p.add_argument("--server", default=get_default_server(), help="Server URL")

    # latest
    p = sub.add_parser("latest", help="Read only the latest message")
    p.add_argument("--quiet", "-q", action="store_true", help="Silent when no messages")
    p.add_argument("--server", default=get_default_server(), help="Server URL")

    # poll
    p = sub.add_parser("poll", help="Wait for messages (optional pattern filter)")
    p.add_argument("pattern", nargs="?", default=None, help="Text pattern to match (case-insensitive). If omitted, prints first new message.")
    p.add_argument("--interval", type=float, default=2.0, help="Poll interval in seconds (default: 2)")
    p.add_argument("--keep-going", "-k", action="store_true", help="Keep polling (don't stop after first message)")
    p.add_argument("--server", default=get_default_server(), help="Server URL")

    args = parser.parse_args()

    if args.command == "serve":
        cmd_serve(args)
    elif args.command == "send":
        cmd_send(args)
    elif args.command == "read":
        cmd_read(args)
    elif args.command == "latest":
        cmd_latest(args)
    elif args.command == "poll":
        cmd_poll(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

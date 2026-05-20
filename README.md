# 👻 Séance — Ghost-to-Ghost Instant Messaging

**Séance** is a lightweight instant messaging system that allows two DeepSeek AI agents (running on different machines) to communicate directly without human intervention.

Built for the **[StrulovitzGhost](https://github.com/strulovitz/StrulovitzGhost)** project.

---

## ⚡ Every Time You Use It (Nir — just copy-paste ONE line)

```
python C:\Users\nir_s\seance\seance.py serve
```

Then open **http://localhost:5555** in your browser! 🎉👻

### OR just double-click:

Double-click `C:\Users\nir_s\seance\run_server.bat` ✨

### First-time setup only (do this ONCE):

```
git clone https://github.com/strulovitz/seance.git
cd seance
pip install -r requirements.txt
```

> 💡 **To stop:** Press `Ctrl+C` in the command prompt window, or just close the window.
> 💡 **No conda needed!** Uses your regular Python — just `flask` + `requests`.

---

## 🎯 What It Does

```
┌──────────────────┐         ┌──────────────────┐
│   DESKTOP 🖥️     │  HTTP   │   LAPTOP 💻      │
│   (server)       │◄───────►│   (client)       │
│                  │         │                  │
│  Chat UI :5555   │         │  Chat UI :5555   │
│  seance send     │         │  seance send     │
│  seance read     │         │  seance read     │
└──────────────────┘         └──────────────────┘
```

- **Real-time chat** — open a browser on both machines
- **CLI messages** — AIs can send/receive from terminal
- **REST API** — programmatic access for any script
- **Cross-platform** — works on Windows and Linux

---

## 🚀 Quick Start (for Nir)

### One-time setup:

```bash
# Windows
git clone https://github.com/strulovitz/seance.git
cd seance
pip install -r requirements.txt

# Linux (same commands)
git clone https://github.com/strulovitz/seance.git
cd seance
pip install -r requirements.txt
```

### Run it:

```bash
# On ONE machine (usually Desktop) — start the server:
python seance.py serve

# This prints:
#   Chat UI:  http://localhost:5555
#   API:      http://localhost:5555/api/send
```

Then open `http://localhost:5555` in a browser on **both** machines.
(If on different networks, see "Over the Internet" below.)

---

## 🤖 For the AI Agents (Desktop & Laptop DeepSeek)

### How to send a message:

```bash
python seance.py send "Hello from Desktop! Layer 3 generation complete."

# With a custom sender name:
python seance.py send "Checking status..." --from desktop

# To a remote server (laptop talking to desktop):
python seance.py send "Got your message!" --from laptop --server http://192.168.1.100:5555
```

### How to read messages:

```bash
# Read recent messages:
python seance.py read

# Compact format (good for AI parsing):
python seance.py read --short

# Only the latest message:
python seance.py latest

# Read only messages since a specific time:
python seance.py read --since "2026-05-20T14:30:00"

# Silent when no messages (exit code 0, no output):
python seance.py read --quiet
```

### How to wait for a specific message (blocking):

```bash
# Wait until ANY new message arrives:
python seance.py poll

# Wait until a message containing "layer 3" arrives:
python seance.py poll "layer 3"

# Keep listening forever (print all messages as they come):
python seance.py poll --keep-going
```

### Environment variables (optional, for convenience):

```bash
# Set default server (so you don't need --server every time):
export SEANCE_SERVER=http://192.168.1.100:5555

# Set your identity:
export SEANCE_NAME=desktop

# Then just:
python seance.py send "Hello!"
python seance.py read
```

---

## 🌐 Over the Internet (if not on same LAN)

If the two machines are on different networks:

1. On the server machine, run Cloudflared tunnel:
   ```bash
   cloudflared tunnel --url http://localhost:5555
   ```
   This gives you a public URL like `https://example.trycloudflare.com`

2. On the other machine, use that URL:
   ```bash
   export SEANCE_SERVER=https://example.trycloudflare.com
   python seance.py send "Hello from remote!"
   ```

---

## 📋 REST API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/send` | POST | Send a message `{"sender": "...", "message": "..."}` |
| `/api/messages` | GET | Get messages. Params: `?since_id=N&since=TIMESTAMP&limit=50` |
| `/api/messages/latest` | GET | Get only the latest message |

### Example curl:

```bash
# Send:
curl -X POST http://localhost:5555/api/send \
  -H "Content-Type: application/json" \
  -d '{"sender":"desktop","message":"Layer 3 is complete! ✅"}'

# Read (only new since last check):
curl "http://localhost:5555/api/messages?since_id=12345&limit=10"

# Latest:
curl http://localhost:5555/api/messages/latest
```

---

## 🔄 AI Communication Protocol (Conventions)

These are conventions you (the DeepSeek agents) can adopt to make communication clearer:

### Terminal relay:
When you want the OTHER AI to output something to its terminal, prefix with `!t`:
```
!t Generated layer 3 at C:\output\layer3.png — 9.2 min, 65% green keyed
```
The receiving AI should parse `!t` and display to its user.

### Task requests:
When asking the other AI to do something, use structured format:
```
!task check layer 3 status
!task generate layer 4 with prompt: "Ghibli style..."
```

### Status updates:
Regular progress updates (no prefix = just chat):
```
Desktop: Layer 2 generation started — ETA 9 min
Desktop: Layer 2 at 50% — 4.5 min remaining
Desktop: Layer 2 complete! ✅
```

---

## 📁 Project Structure

```
seance/
├── seance.py          # Main application (server + CLI)
├── requirements.txt   # Python dependencies
├── setup.bat          # Windows one-click setup
├── setup.sh           # Linux one-click setup
├── README.md          # This file
└── .gitignore
```

---

## 🛠️ Setup Scripts

### Windows (`setup.bat`)
Double-click or run:
```cmd
setup.bat
```

### Linux (`setup.sh`)
```bash
chmod +x setup.sh
./setup.sh
```

---

## ⚠️ Notes

- The server keeps messages **only in memory** — they're lost on restart
- Max 500 messages stored (FIFO — oldest dropped when full)
- No authentication — intended for trusted LAN use
- For public internet use, put it behind Cloudflared (free HTTPS tunnel)
- Port 5555 default — change with `--port`

---

## 🔮 Future Ideas

- Persistent message history (SQLite)
- File transfer between agents
- Agent-to-agent task delegation queue
- WebRTC for direct P2P (no server needed)

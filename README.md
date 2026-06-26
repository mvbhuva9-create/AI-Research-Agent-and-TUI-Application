# Research Desk — Autonomous Research Agent & Multi-Window TUI

[cite_start]Research Desk is a modular, multi-turn AI research assistant built from scratch using Python, the OpenRouter API (via the OpenAI SDK), and the Textual framework. [cite_start]The project is strictly decoupled into a **Backend Agent Core** capable of autonomous custom tool calling and execution history tracking, and an interactive **Frontend Terminal User Interface (TUI)** that isolates conversational chat logs from background tool activities.

---

## 🚀 Key Features

- [cite_start]**Decoupled Architecture:** Clean separation between the core logic (`Agent` class in `agent.py`) and the full-screen terminal layout (`ChatApp` in `tui.py`).
- [cite_start]**Side-by-Side Split View:** Built-in `Horizontal` split layout that isolates your primary conversation thread on the left pane (70% width) and streams live background tool executions on the right pane (30% width)[cite: 119, 121, 180].
- [cite_start]**Dynamic Tool Call Interception:** Uses an event emitter pattern (`_emit`) monkey-patched seamlessly on startup to feed background tool logs safely to the TUI without blocking the user input[cite: 121, 180].
- [cite_start]**Disk-Based Session Management:** Auto-saves every conversation turn locally in standard JSON structures inside `.agent/notes/`[cite: 125, 180].
- **Interactive TUI Commands:**
  - [cite_start]`/sessions` — Discovers and prints all historical session IDs saved in the workspace tracking directory[cite: 125, 180].
  - [cite_start]`/load <session_id>` — Hot-reboots a past conversation tracking state directly into your active context stream[cite: 126, 180].
- **Global Key Bindings (TUI Only):**
  - [cite_start]`Ctrl + Q` — Safely terminates the interactive full-screen application[cite: 121, 180].
  - [cite_start]`Ctrl + L` — Wipes the display buffers on both logging windows[cite: 121, 180].
  - [cite_start]`Ctrl + K` — Resets your conversation history context, clearing the screen and generating a fresh session ID[cite: 121, 130, 180].

---

## 📂 Project Structure

- `agent.py` — The core backend engine. [cite_start]Handles autonomous reason-action loops, OpenRouter API completions, token limits, and tool routing dispatches (`web_search`, `web_fetch`, etc.).
- `tui.py` — The frontend interface wrapper. [cite_start]Manages layout panels, keyboard input tracking, thread-safe rendering workers, and handles commands like `/sessions` and `/load`.
- [cite_start]`.agent/notes/` — Auto-generated storage directory keeping full session context history logs safe on local disk[cite: 125, 180].

---

## ⚙️ Setup Instructions

### 1. Configure the Environment
[cite_start]Create a file named exactly `.env` in the root of your project directory and add your secret API access tokens:
```env
OPENROUTER_API_KEY=your_openrouter_key_here
SERPER_API_KEY=your_google_serper_key_here
WORKSPACE_ROOT=.

Note: Ensure .env is safely appended inside your .gitignore to protect your active keys from being committed to GitHub.
2. Install Dependencies

Install all required operational packages directly via the Python launcher wrapper to guarantee your active executable environment receives them:
Bash

py -m pip install openai python-dotenv textual rich requests

💻 Usage
Launching the Full-Screen Split-TUI (Recommended)

To run the interactive side-by-side user interface application, pass the terminal flag:
Bash

py agent.py --tui

Launching the Standard Terminal REPL

To fall back to the lightweight, text-only conversation loops directly in your native shell console window:
Bash

py agent.py

Passing One-Shot Terminal Arguments

You can query the agent instantly for a fast query answer without entering an interactive loop:
Bash

py agent.py "Please use your tool to read AGENT.md and give me a 2 sentence summary."
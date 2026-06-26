# Research Desk — Autonomous Research Agent & Multi-Window TUI

Research Desk is a modular, multi-turn AI research assistant built from scratch using Python, the OpenRouter API (via the OpenAI SDK), and the Textual framework. The project is cleanly decoupled into an autonomous **Backend Agent Core** capable of custom tool execution and state persistence, and an interactive, full-screen **Frontend Terminal User Interface (TUI)** that separates conversation chat streams from live background tool operations.

---

## 🚀 Key Features

- **Decoupled Architecture:** Clean structural separation between the core operational logic (`Agent` class in `agent.py`) and the full-screen interactive layout (`ChatApp` class in `tui.py`).
- **Multi-Window TUI Split Layout:** Utilizes Textual's horizontal layouts to split your view into a primary conversation chat logs panel (left side, 70% width) and a dedicated live tool status tracking pane (right side, 30% width).
- **Dynamic Tool Hook Interception:** Intercepts background execution steps by overriding the private event emitter method (`_emit`) on startup, routing tool status metrics directly to the secondary panel in a thread-safe manner without locking the UI.
- **Disk-Based Session Management:** Automatically maintains conversation session states, persistent tracking variables, and chat histories inside local JSON structures stored on disk under `.agent/notes/`.
- **Interactive In-App TUI Commands:**
  - `/sessions` — Enumerate and discover all active and historical session identifiers saved in your notes directory.
  - `/load <session_id>` — Hot-reload a past conversation tracking state directly into your active context stream to resume work.
- **Global Key Bindings:**
  - `Ctrl + Q` — Safely terminates the interactive full-screen TUI application.
  - `Ctrl + L` — Wipes the display logging buffers on both panes instantly.
  - `Ctrl + K` — Resets your conversation history context, clearing the display and spinning up a fresh session ID.

---

## 📂 Project Structure

- **`agent.py`** — The backend engine. Houses the core reason-action loop (`_run_loop`), OpenRouter completion dispatches, automatic context saving routines, and native tool orchestration contracts. Includes tools for web searches (Serper API), webpage fetching/scraping, relative workspace file manipulation (`read_file`, `write_file`, `edit_file`, `list_files`), and academic literature extraction (`paper_search`, `read_paper`).
- **`tui.py`** — The frontend client interface wrapper. Configures the CSS grid widths, initializes event tracking workers, binds keyboard shortcuts, and safely manages thread responses back into the UI log.
- **`.agent/notes/`** — Local persistent directory footprints containing historical session backup records.

---

## ⚙️ Setup Instructions

### 1. Configure Your Environment Variables
Create a file named exactly `.env` in the root of your project directory and add your secret API access credentials:
```env
OPENROUTER_API_KEY=your_openrouter_api_key_here
SERPER_API_KEY=your_google_serper_api_key_here
WORKSPACE_ROOT=.
```
2. Install Project Dependencies

Install all required operational packages directly in your active terminal environment using the Python launcher wrapper to ensure proper path mapping:
```Bash

py -m pip install openai python-dotenv textual rich requests
```
💻 Usage
Launching the Multi-Window Split-TUI (Recommended)

To run the full-screen side-by-side conversational window panels:
```Bash

py agent.py --tui
```
Launching the Standard Terminal REPL

To run a classic lightweight conversation loop directly inside your native shell console window:
```Bash

py agent.py
```
Passing One-Shot Terminal Arguments

To query the agent for an immediate standalone answer from your shell without opening an interactive view loop:
```Bash

py agent.py "Please use your tool to open TODO.md and tell me what tasks are left."
```

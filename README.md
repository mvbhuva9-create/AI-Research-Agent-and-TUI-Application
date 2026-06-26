
RESEARCH DESK — AUTONOMOUS RESEARCH AGENT & MULTI-WINDOW TUI


Research Desk is a modular, multi-turn AI research assistant built from 
scratch using Python, the OpenRouter API, and the Textual framework. 
The project is decoupled into an autonomous Backend Agent Core capable 
of custom tool execution, and an interactive, full-screen Frontend 
Terminal User Interface (TUI) that separates conversation chat streams 
from live background tool operations.

------------------------------------------------------------------------
KEY FEATURES
------------------------------------------------------------------------

* Decoupled Architecture: Clean separation between the core operational 
  logic (Agent class in agent.py) and the full-screen interactive 
  layout (ChatApp class in tui.py).
  
* Multi-Window TUI Split Layout: Splits your view into a primary 
  conversation panel (left side, 70% width) and a dedicated live tool 
  status tracking pane (right side, 30% width).
  
* Dynamic Tool Hook Interception: Intercepts background execution steps 
  by overriding the private event emitter method (_emit) on startup, 
  routing tool metrics directly to the secondary panel without locking 
  up the primary chat interface.
  
* Disk-Based Session Management: Automatically maintains conversation 
  session states and histories inside local JSON structures stored on 
  disk under the .agent/notes/ directory.

* Interactive In-App TUI Commands:
  - /sessions : Enumerate and discover all active and historical 
    session identifiers saved in your notes directory.
  - /load <id> : Hot-reload a past conversation tracking state directly 
    into your active context stream to resume work.

* Global Key Bindings:
  - Ctrl + Q : Safely terminates the interactive full-screen TUI.
  - Ctrl + L : Wipes the display logging buffers on both panes instantly.
  - Ctrl + K : Resets your conversation history context, clearing the 
    display and spinning up a fresh session ID.

------------------------------------------------------------------------
PROJECT STRUCTURE
------------------------------------------------------------------------

- agent.py       : The backend engine. Houses the core reason-action loop,
                   OpenRouter completions, automatic context saving, 
                   and tool orchestration contracts (web_search, 
                   web_fetch, file handling, paper_search).
                   
- tui.py         : The frontend client interface wrapper. Configures the 
                   CSS grid splits, binds keyboard shortcuts, and safely 
                   manages thread responses back into the UI log widgets.
                   
- .agent/notes/  : Local directory footprint housing persistent backup 
                   session JSON files.

------------------------------------------------------------------------
SETUP INSTRUCTIONS
------------------------------------------------------------------------

1. Configure Your Environment Variables
Create a file named exactly .env in the root of your project directory 
and add your secret API access credentials:

OPENROUTER_API_KEY=your_openrouter_api_key_here \n
SERPER_API_KEY=your_google_serper_api_key_here \n
WORKSPACE_ROOT=. \n

2. Install Project Dependencies
Run the following command in your terminal to ensure proper path mapping:

py -m pip install openai python-dotenv textual rich requests

------------------------------------------------------------------------
USAGE COMMANDS
------------------------------------------------------------------------

* Launching the Multi-Window Split-TUI (Recommended):
  py agent.py --tui

* Launching the Standard Terminal REPL:
  py agent.py

* Passing One-Shot Terminal Arguments:
  py agent.py "Please use your tool to open AGENT.md and summarize it."


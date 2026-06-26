"""
TUIAgent — full-screen Textual UI inheriting from Agent.

Usage:
  python agent.py --tui

Tasks:
  1. class TUIAgent(Agent) — override _emit() for tool log panel
  2. class ResearchDeskApp(App) — layout, input, key bindings
  3. on_input_submitted -> worker -> self.chat() (inherited from Agent)
  4. Ctrl+L / Ctrl+K / Ctrl+Q from Week 2
"""
from agent import   Agent
import os
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Header, Footer, Input, RichLog
from textual.containers import Vertical, Horizontal
MAX_HISTORY_TURNS=20


 # keep last N user+assistant pairs

# ---------------------------------------------------------------------------
# Chat logic (reuse / adapt from your Week 1 submission)
# ---------------------------------------------------------------------------




def trim_history(messages: list[dict], max_turns: int) -> list[dict]:
    trimmed=[]
    trimmed.append(messages[0])
    if len(messages) -1 <= max_turns*2:
        return messages
    else:
        trimmed.extend(messages[-max_turns*2:])
        return trimmed


# ---------------------------------------------------------------------------
# TUI
# ---------------------------------------------------------------------------

class ChatApp(App):
    """A full-screen terminal chatbot."""

    TITLE = "Research Agent"
    CSS = """
    Screen {
        layout: vertical;
    }

    .split-layout {
        layout: horizontal;
        height: 1fr;
    }

    #log {
        width: 70%;
        border: solid $primary;
        padding: 0 1;
    }

    #tool-pane {
        width: 30%;
        border: dashed $secondary;
        padding: 0 1;
        background: $surface;
    }

    Input {
        dock: bottom;
        height: 3;
    }
    
    """

    BINDINGS = [
        Binding("ctrl+l", "clear_display", "Clear display"),
        Binding("ctrl+k", "clear_history", "Clear history"),
        Binding("ctrl+q", "quit", "Quit"),
    ]

    def __init__(self):
        super().__init__()
        self.agent=Agent()
        self.messages=list(self.agent.messages)
        self.agent._emit = self.tui_emit

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal(classes="split-layout"):
          yield RichLog(id="log", wrap=True, markup=True, highlight=True)
          yield RichLog(id="tool-pane", wrap=True, markup=True, highlight=True)
        yield Input(placeholder="Type a message and press Enter...")
        yield Footer()

    def on_mount(self) -> None:
        log = self.query_one("#log", RichLog)
        log.write("[bold green]Chat started.[/bold green] Ctrl+Q to quit, Ctrl+L to clear, Ctrl+k to clear history.\n")
        self.query_one(Input).focus()

    def tui_emit(self, event: str, **data) -> None:
            """Intercepts internal agent execution calls and prints them to the second window."""
            if event == "tool_call":
                tool_name = data.get("name", "unknown")
                self.call_from_thread(
                    lambda: self.query_one("#tool-pane", RichLog).write(
                        f"[bold yellow]→ [Executing Tool]:[/bold yellow] [cyan]{tool_name}[/cyan]\n"
                    )
                )
    # -----------------------------------------------------------------------
    # Event handlers
    # -----------------------------------------------------------------------

    def on_input_submitted(self, event: Input.Submitted) -> None:
        log = self.query_one("#log", RichLog)
        event.input.clear()
        user_text = event.value.strip()
        if not user_text:
            return
        if user_text == "/sessions":
          from agent import SESSIONS_DIR # Local directory fallback matching context flags
          if os.path.exists(SESSIONS_DIR):
              files = [f for f in os.listdir(SESSIONS_DIR) if f.endswith(".json")]
              log.write(f"[bold cyan]Available Sessions:[/bold cyan]\n" + "\n".join([f" - {f[:-5]}" for f in files]))
          else:
              log.write(f"[bold red]No sessions folder directory established yet.[/bold red]")
          return
        elif user_text.startswith("/load "):
          try:
            target_session = user_text.split(" ")[1].strip()
            self.agent = Agent(session_id=target_session)
            self.agent._emit = self.tui_emit 
            self.messages = list(self.agent.messages)
            log.write(f"[bold green]Successfully switched context stream! Active session:[/bold green] [{self.agent.session_id}]")
          except Exception as e:
            log.write(f"[bold red]Error in switching context stream:[/bold red]"+str(e))
          return

      
        log.write(f"[bold cyan][You][/bold cyan] {user_text}\n")

        # Append user message to history
        self.messages.append({"role": "user", "content": user_text})
        self.messages = trim_history(self.messages, MAX_HISTORY_TURNS)
        self.run_worker(self._get_response, thread=True)
        # Run the API call in a background thread so the UI stays responsive
        # TODO: call self.run_worker(self._get_response(), thread=True)
        pass

    async def _get_response(self) -> None:
    
        
        try:
            reply=self.agent.chat(self.messages[-1]["content"])
            self.messages.append({"role": "assistant", "content": reply})
            self.call_from_thread(
                lambda: self.query_one("#log", RichLog).write(f"[bold magenta][Agent][/bold magenta] {reply}\n")
            )
        except Exception as e:
            self.call_from_thread(
                lambda: self.query_one("#log", RichLog).write(f"[bold red]Error: {e}[/bold red]\n")
            )
        # TODO: implement
        pass

    # -----------------------------------------------------------------------
    # Actions (bound to keyboard shortcuts)
    # -----------------------------------------------------------------------

    def action_clear_display(self) -> None:
       
        log = self.query_one("#log", RichLog)
        log.clear()
        pass

    def action_clear_history(self) -> None:
       
        log = self.query_one("#log", RichLog)
        self.agent = Agent() 
        self.messages = list(self.agent.messages)
        log.clear()
        log.write(f"[bold yellow]Context cleared. New Session initialized: {self.agent.session_id}[/bold yellow]\n\n")
        pass


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    ChatApp().run()

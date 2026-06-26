import os
import sys
import json
import uuid  
from datetime import datetime, timezone  
from openai import OpenAI
from dotenv import load_dotenv

# Import custom tool functions
from tools.files import read_file, edit_file, write_file, list_files
from tools.web import web_search, web_fetch
from tools.papers import paper_search, read_paper

load_dotenv()
serp_key = os.environ.get("SERPER_API_KEY", "")

WORKSPACE_ROOT = os.path.abspath(os.environ.get("WORKSPACE_ROOT", "."))
MAX_ITERATIONS = 10
MAX_READ_CHARS = 12_000
SESSIONS_DIR = os.path.join(WORKSPACE_ROOT, ".agent", "notes")

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search Google to retrieve real-time facts. Formulate a single, concise keyword search phrase instead of a conversational sentence. Do not call this tool multiple times in parallel for the same basic question.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query query question string."}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "web_fetch",
            "description": "Extract and read the full text content from a specific webpage URL destination.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "The complete web address link starting with http/https."}
                },
                "required": ["url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Open and read a file securely from within the allowed workspace layout grid.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "The target relative path file location."},
                    "start_line": {"type": "integer", "default": 1},
                    "read_lines": {"type": "integer", "default": 200}
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Create a brand new file or overwrite an existing file with fresh content.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Destination workspace relative path file code output."},
                    "content": {"type": "string", "description": "The payload content context buffer string."}
                },
                "required": ["path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "edit_file",
            "description": "Modify, replace, append, or delete targeted lines inside an existing document.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "operation": {"type": "string", "enum": ["replace", "delete", "append"]},
                    "start_line": {"type": "integer"},
                    "end_line": {"type": "integer"},
                    "content": {"type": "string"}
                },
                "required": ["path", "operation", "start_line"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "Enumerate and discover files within a designated workspace directory folder.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "default": "."},
                    "pattern": {"type": "string", "default": "*"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "paper_search",
            "description": "Query Hugging Face Daily Papers engine for academic resources matching keywords.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "limit": {"type": "integer", "default": 5}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_paper",
            "description": "Download and extract complete technical texts from arXiv using an ID coordinate index.",
            "parameters": {
                "type": "object",
                "properties": {
                    "paper_id": {"type": "string"},
                    "start_page": {"type": "integer", "default": 1},
                    "max_pages": {"type": "integer", "default": 5}
                },
                "required": ["paper_id"]
            }
        }
    }
]

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY", "mock-key"),
)
MODEL = "openrouter/free"
BASE_PROMPT = "You are Research Desk, a helpful research assistant."

# --- Standalone Session Helpers (Fixes Scope/Indentation bugs) ---

def create_session() -> str:
    os.makedirs(SESSIONS_DIR, exist_ok=True)
    return uuid.uuid4().hex[:8]

def build_system_prompt() -> str:
    current_date = datetime.now().strftime("%A, %B %d, %Y")
    date_prompt = f"\n\nCurrent Context: Today is {current_date}. All relative time queries refer to this date."
    filepath = os.path.join(WORKSPACE_ROOT, "AGENT.md")
    BASE_PROMPT = "You are Research Desk, a helpful research assistant."
    BASE_PROMPT=BASE_PROMPT+date_prompt
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return BASE_PROMPT + "\n\n" + f.read()
        except Exception:
            return BASE_PROMPT
    return BASE_PROMPT

def save_session(session_id: str, messages: list, title: str = "Untitled") -> None:
    os.makedirs(SESSIONS_DIR, exist_ok=True)
    filepath = os.path.join(SESSIONS_DIR, f"{session_id}.json")
    now_iso = datetime.now(timezone.utc).isoformat()
    created_at = now_iso
    
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                old_data = json.load(f)
                created_at = old_data.get("created_at", now_iso)
        except Exception as e:
            print(f"Error reading existing session: {e}", file=sys.stderr)

    session = {
        "id": session_id,
        "title": title,
        "created_at": created_at,
        "updated_at": now_iso,
        "messages": messages
    }
    
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(session, f, indent=2)
    except Exception as e:
        print(f"Error in saving session: {e}", file=sys.stderr)

def load_session(session_id: str) -> dict:
    filepath = os.path.join(SESSIONS_DIR, f"{session_id}.json")
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error in loading session: {e}", file=sys.stderr)
    return {"messages": []}


# --- Dynamic Agent Core Processing ---

class Agent:
    """Core agent: loop, tools, sessions. No UI."""
    
    def __init__(self, workspace: str = ".", session_id: str | None = None):
        self.workspace = os.path.abspath(workspace)
        
        if session_id is None:
            self.session_id = create_session()
            self.messages = []
            # Fix 4: Properly evaluated execution parentheses tracker ()
            self.messages.append({"role": "system", "content": build_system_prompt()})
        else:
            self.session_id = session_id
            session_data = load_session(session_id)
            # Fix 3: Handle structural load variations gracefully
            self.messages = session_data.get("messages", [])

    def chat(self, user_message: str) -> str:
        self.messages.append({"role": "user", "content": user_message})
        save_session(self.session_id, self.messages)
        return self._run_loop()

    def run_once(self, prompt: str) -> str:
        return self.chat(prompt)

    def _run_loop(self) -> str:
        for _ in range(MAX_ITERATIONS):
            response = client.chat.completions.create(
                model=MODEL,
                messages=self.messages,
                tools=TOOLS,
            )
            message = response.choices[0].message
            finish_reason = response.choices[0].finish_reason
            
            if finish_reason == "tool_calls":
                self.messages.append(message.to_dict())
                for tool_call in message.tool_calls:
                    self._emit("tool_call", name=tool_call.function.name)
                    c = self.dispatch(tool_call)
                    self.messages.append({
                        "role": "tool", 
                        "tool_call_id": tool_call.id, 
                        "content": c
                    })
                continue

            elif finish_reason == "stop" or finish_reason is None:
                self.messages.append(message.to_dict())
                save_session(self.session_id, self.messages)
                return message.content if message.content else "Execution completed."
            else:
                return "Error: Unexpected termination reason."
        return "Error: Max reasoning execution cycles exceeded."

    def dispatch(self, tool_call) -> str:
        try:
            args = json.loads(tool_call.function.arguments)
            name = tool_call.function.name
            
            if name == "web_search":
                returned = web_search(args["query"])
            elif name == "web_fetch":
                returned = web_fetch(args["url"])
            elif name == "paper_search":
                returned = paper_search(args["query"], args.get("limit", 5))
            elif name == "read_paper":
                returned = read_paper(args["paper_id"], args.get("start_page", 1), args.get("max_pages", 5))
            elif name == "write_file":
                returned = write_file(args["path"], args["content"])
            elif name == "read_file":
                returned = read_file(args["path"], args.get("start_line", 1), args.get("read_lines", 200))
            elif name == "edit_file":
                returned = edit_file(args["path"], args["operation"], args["start_line"], args.get("end_line"), args.get("content"))
            elif name == "list_files":
                returned = list_files(args.get("path", "."), args.get("pattern", "*"))
            else:
                return '{"error": "Unknown tool function call executed."}'
        except Exception as e:
            return json.dumps({"error": str(e)})
            
        return json.dumps(returned)

    def _emit(self, event: str, **data) -> None:
        """Override in subclass configurations for printing metrics."""
        pass


class REPLAgent(Agent):
    """Terminal REPL + one-shot CLI interface wrapper handles UI parsing."""

    def run(self) -> None:
        print(f"Research Desk [{self.session_id}] — /quit to exit")
        while True:
            try:
                user_input = input("> ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                break
            if not user_input or user_input in ("/quit", "/exit"):
                break
            # --- NEW: ADD REPL-LEVEL SESSION INTERCEPT COMMANDS ---
            
            # Command 1: Let the user see session keys instantly without calling the AI
            if user_input == "/sessions":
                from agent import SESSIONS_DIR # Local directory fallback matching context flags
                if os.path.exists(SESSIONS_DIR):
                    files = [f for f in os.listdir(SESSIONS_DIR) if f.endswith(".json")]
                    print("Available Sessions:\n" + "\n".join([f" - {f[:-5]}" for f in files]))
                else:
                    print("No sessions folder directory established yet.")
                continue

            # Command 2: Let the user jump back to a historical state tracking file
            if user_input.startswith("/load "):
                target_session = user_input.split(" ")[1].strip()
                # Re-initialize the current instance to load the fresh messages array payload
                self.__init__(workspace=self.workspace, session_id=target_session)
                print(f"Successfully switched context stream! Active session: [{self.session_id}]")
                continue
            print(self.chat(user_input))
            print()

    def _emit(self, event: str, **data) -> None:
        if event == "tool_call":
            print(f"   [tool executing] -> {data.get('name')}", file=sys.stderr)


def main():
    # Setup optional session parsing from CLI args array tracking flags
    session_arg = None
    if "--tui" in sys.argv:
        try:
            from tui import ChatApp
            app = ChatApp()
            app.run()
            return
        except ImportError:
            print("Error: Could not find tui.py or ChatApp. Ensure tui.py is in the same directory.", file=sys.stderr)
    if "--session" in sys.argv:
        try:
            idx = sys.argv.index("--session")
            session_arg = sys.argv[idx + 1]
            sys.argv.pop(idx)
            sys.argv.pop(idx)
        except Exception:
            pass

    agent = REPLAgent(session_id=session_arg)
    if len(sys.argv) > 1 :
        print(agent.run_once(" ".join(sys.argv[1:])))
        return
    agent.run()


if __name__ == "__main__":
    main()
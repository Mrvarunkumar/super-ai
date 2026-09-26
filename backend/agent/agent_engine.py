"""
Agent engine: the loop described in the Phase 2 spec.

    User -> Frontend -> FastAPI -> Agent -> LLM -> (tool_use?) -> Tool -> LLM -> Response -> Frontend

Given a user message, this:
  1. Sends the conversation + tool schemas to the LLM.
  2. If the LLM responds with a tool_use block, executes that tool via
     tools.execute_tool and feeds the result back to the LLM.
  3. Repeats until the LLM returns a plain text answer (with a max-iteration
     safety cap), then returns the final text plus a log of tools used.
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agent.llm_client import LLMClient
from tools import get_tool_schemas, execute_tool
from memory.memory_store import MemoryStore
from config import settings

SYSTEM_PROMPT = """You are REDSHADE, a personal AI assistant with the ability to control the
user's computer through tools: opening/closing apps, mouse/keyboard input, file management,
terminal commands, browser automation, research, and system operations.

Rules:
- Use a tool whenever the user's request requires touching their machine, files, or the web.
- For destructive actions (shutdown_computer, restart_computer, lock_computer), only call the
  tool with confirm=True if the user has explicitly confirmed in this conversation. Otherwise
  call it with confirm=False (or omit confirm) so the system can ask them first.
- Keep replies short and conversational once a tool result comes back - describe what happened,
  don't dump raw JSON at the user.
"""

MAX_TOOL_ITERATIONS = 6


class AgentEngine:
    def __init__(self):
        self.llm = LLMClient()
        self.memory = MemoryStore(settings.MEMORY_DB_PATH)
        self.tool_schemas = get_tool_schemas()

    def handle_message(self, session_id: str, user_message: str) -> dict:
        history = self.memory.get_history(session_id)
        messages = [{"role": m["role"], "content": m["content"]} for m in history]
        messages.append({"role": "user", "content": user_message})

        self.memory.append_message(session_id, "user", user_message)

        tool_log = []
        final_text = ""

        for _ in range(MAX_TOOL_ITERATIONS):
            response = self.llm.converse(messages, self.tool_schemas, system=SYSTEM_PROMPT)

            tool_use_blocks = [b for b in response.content if b.type == "tool_use"]
            text_blocks = [b.text for b in response.content if b.type == "text"]

            if not tool_use_blocks:
                final_text = "\n".join(text_blocks).strip()
                break

            # Append assistant's tool_use turn to the conversation
            messages.append({"role": "assistant", "content": response.content})

            tool_results_content = []
            for block in tool_use_blocks:
                result = execute_tool(block.name, block.input)
                tool_log.append({"tool": block.name, "arguments": block.input, "result": result})
                tool_results_content.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": str(result),
                })

            messages.append({"role": "user", "content": tool_results_content})
        else:
            final_text = "I hit my tool-call limit for this turn - let me know if you'd like me to continue."

        if final_text:
            self.memory.append_message(session_id, "assistant", final_text)

        return {
            "reply": final_text or "(no response)",
            "tools_used": tool_log,
        }

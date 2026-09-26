"""
Thin wrapper around the Anthropic API. Two entry points:
  - simple_complete(prompt): plain text in, plain text out (used by research.py)
  - converse(messages, tools): full tool-use turn (used by agent_engine.py)
"""
import sys
import os
import anthropic

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import settings


class LLMClient:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = settings.MODEL_NAME

    def simple_complete(self, prompt: str) -> str:
        resp = self.client.messages.create(
            model=self.model,
            max_tokens=settings.MAX_TOKENS,
            messages=[{"role": "user", "content": prompt}],
        )
        return "".join(block.text for block in resp.content if block.type == "text")

    def converse(self, messages: list, tools: list, system: str = None):
        """
        One turn of the conversation, with tool-use enabled.
        Returns the raw Anthropic response object; the agent engine decides
        whether to execute a tool_use block and loop again.
        """
        kwargs = dict(
            model=self.model,
            max_tokens=settings.MAX_TOKENS,
            messages=messages,
            tools=tools,
        )
        if system:
            kwargs["system"] = system
        return self.client.messages.create(**kwargs)

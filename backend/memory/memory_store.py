"""
Lightweight JSON-file memory store.
Swap this for SQLite/Postgres later without changing the calling code's shape.
"""
import json
import os
import threading
from typing import Any, Dict, List

_lock = threading.Lock()


class MemoryStore:
    def __init__(self, path: str):
        self.path = path
        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
        if not os.path.exists(self.path):
            self._write({"kv": {}, "conversations": {}})

    def _read(self) -> Dict[str, Any]:
        with _lock:
            with open(self.path, "r", encoding="utf-8") as f:
                return json.load(f)

    def _write(self, data: Dict[str, Any]) -> None:
        with _lock:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

    # ---- key/value memory ----
    def set(self, key: str, value: Any) -> None:
        data = self._read()
        data["kv"][key] = value
        self._write(data)

    def get(self, key: str, default: Any = None) -> Any:
        return self._read()["kv"].get(key, default)

    def all(self) -> Dict[str, Any]:
        return self._read()["kv"]

    # ---- conversation history ----
    def append_message(self, session_id: str, role: str, content: str) -> None:
        data = self._read()
        data["conversations"].setdefault(session_id, [])
        data["conversations"][session_id].append({"role": role, "content": content})
        self._write(data)

    def get_history(self, session_id: str) -> List[Dict[str, str]]:
        return self._read()["conversations"].get(session_id, [])

    def clear_history(self, session_id: str) -> None:
        data = self._read()
        data["conversations"][session_id] = []
        self._write(data)

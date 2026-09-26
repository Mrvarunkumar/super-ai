"""
Long-running task tracking (Days 66-70). This is a lightweight in-process
manager: tasks are dicts persisted to memory/tasks_store.json so /tasks GET
survives a restart. Actual background execution (running each step against
the AgentEngine) is left as a TODO hook - wire it to a background thread /
asyncio task / Celery worker depending on how heavy your steps get.
"""
import sys
import os
import uuid
import json
import threading

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import settings

_lock = threading.Lock()


class TaskManager:
    def __init__(self, path: str = None):
        self.path = path or settings.TASKS_DB_PATH
        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
        if not os.path.exists(self.path):
            self._write({})

    def _read(self):
        with _lock:
            with open(self.path, "r", encoding="utf-8") as f:
                return json.load(f)

    def _write(self, data):
        with _lock:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

    def create_task(self, title: str, steps: list) -> dict:
        task_id = str(uuid.uuid4())[:8]
        task = {
            "id": task_id,
            "title": title,
            "steps": [{"description": s, "done": False} for s in steps],
            "status": "pending",
            "progress": 0.0,
            "result": None,
        }
        data = self._read()
        data[task_id] = task
        self._write(data)
        return task

    def list_tasks(self) -> list:
        return list(self._read().values())

    def get_task(self, task_id: str):
        return self._read().get(task_id)

    def update_status(self, task_id: str, status: str) -> dict:
        data = self._read()
        if task_id not in data:
            return {"success": False, "error": "Task not found."}
        data[task_id]["status"] = status
        self._write(data)
        return {"success": True, "task": data[task_id]}

    def mark_step_done(self, task_id: str, step_index: int) -> dict:
        data = self._read()
        if task_id not in data:
            return {"success": False, "error": "Task not found."}
        steps = data[task_id]["steps"]
        if step_index >= len(steps):
            return {"success": False, "error": "Step index out of range."}
        steps[step_index]["done"] = True
        done_count = sum(1 for s in steps if s["done"])
        data[task_id]["progress"] = round(done_count / len(steps), 2) if steps else 1.0
        if done_count == len(steps):
            data[task_id]["status"] = "done"
        self._write(data)
        return {"success": True, "task": data[task_id]}

    def pause(self, task_id: str) -> dict:
        return self.update_status(task_id, "paused")

    def resume(self, task_id: str) -> dict:
        return self.update_status(task_id, "running")

    def cancel(self, task_id: str) -> dict:
        return self.update_status(task_id, "cancelled")

    def retry(self, task_id: str) -> dict:
        data = self._read()
        if task_id not in data:
            return {"success": False, "error": "Task not found."}
        for step in data[task_id]["steps"]:
            step["done"] = False
        data[task_id]["progress"] = 0.0
        data[task_id]["status"] = "pending"
        self._write(data)
        return {"success": True, "task": data[task_id]}

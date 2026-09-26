"""
FastAPI backend - the API layer between the frontend and the Agent Engine.

    frontend -> FastAPI -> Agent Engine -> LLM + Tools

Run with:  uvicorn main:app --reload --host 0.0.0.0 --port 8000
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import psutil

from config import settings
from models import (
    ChatRequest, ChatResponse, CommandRequest, CommandResponse,
    StatusResponse, Task, TaskCreateRequest, MemoryEntry,
)
from agent.agent_engine import AgentEngine
from agent.task_manager import TaskManager
from tools import execute_tool, get_tool_schemas
from memory.memory_store import MemoryStore

app = FastAPI(title="REDSHADE Backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agent = AgentEngine()
tasks = TaskManager()
memory = MemoryStore(settings.MEMORY_DB_PATH)


@app.get("/")
def root():
    return {"service": "REDSHADE backend", "status": "online"}


# ---------------- CHAT ----------------
@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    try:
        result = agent.handle_message(req.session_id, req.message)
        tool_used = result["tools_used"][-1]["tool"] if result["tools_used"] else None
        tool_result = result["tools_used"][-1]["result"] if result["tools_used"] else None
        return ChatResponse(reply=result["reply"], tool_used=tool_used, tool_result=tool_result, state="IDLE")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------- DIRECT COMMAND (bypasses the LLM, calls a tool by name) ----------------
@app.post("/command", response_model=CommandResponse)
def command(req: CommandRequest):
    if req.tool in settings.SENSITIVE_ACTIONS and not req.confirm:
        return CommandResponse(
            tool=req.tool, success=False, requires_confirmation=True,
            message=f"'{req.tool}' requires confirm=True to execute.",
        )
    args = dict(req.arguments)
    if req.tool in settings.SENSITIVE_ACTIONS:
        args["confirm"] = req.confirm
    result = execute_tool(req.tool, args)
    return CommandResponse(tool=req.tool, success=bool(result.get("success", result.get("executed", False))), result=result)


# ---------------- STATUS ----------------
@app.get("/status", response_model=StatusResponse)
def status():
    batt = psutil.sensors_battery()
    net_up = any(s.isup for s in psutil.net_if_stats().values())
    return StatusResponse(
        online=True,
        cpu_percent=psutil.cpu_percent(interval=0.2),
        ram_percent=psutil.virtual_memory().percent,
        disk_percent=psutil.disk_usage("/").percent,
        battery_percent=(batt.percent if batt else None),
        network_online=net_up,
        active_tasks=len([t for t in tasks.list_tasks() if t["status"] in ("pending", "running")]),
        tools_available=len(get_tool_schemas()),
    )


# ---------------- TASKS ----------------
@app.get("/tasks")
def list_tasks():
    return tasks.list_tasks()


@app.post("/tasks", response_model=Task)
def create_task(req: TaskCreateRequest):
    return tasks.create_task(req.title, req.steps)


@app.post("/tasks/{task_id}/pause")
def pause_task(task_id: str):
    return tasks.pause(task_id)


@app.post("/tasks/{task_id}/resume")
def resume_task(task_id: str):
    return tasks.resume(task_id)


@app.post("/tasks/{task_id}/cancel")
def cancel_task(task_id: str):
    return tasks.cancel(task_id)


@app.post("/tasks/{task_id}/retry")
def retry_task(task_id: str):
    return tasks.retry(task_id)


@app.post("/tasks/{task_id}/steps/{step_index}/complete")
def complete_step(task_id: str, step_index: int):
    return tasks.mark_step_done(task_id, step_index)


# ---------------- MEMORY ----------------
@app.get("/memory")
def get_memory():
    return memory.all()


@app.post("/memory")
def set_memory(entry: MemoryEntry):
    memory.set(entry.key, entry.value)
    return {"success": True}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=True)

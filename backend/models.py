from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict
from enum import Enum


class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"


class ChatResponse(BaseModel):
    reply: str
    tool_used: Optional[str] = None
    tool_result: Optional[Any] = None
    state: str = "IDLE"


class CommandRequest(BaseModel):
    tool: str
    arguments: Dict[str, Any] = Field(default_factory=dict)
    confirm: bool = False


class CommandResponse(BaseModel):
    tool: str
    success: bool
    result: Any = None
    requires_confirmation: bool = False
    message: Optional[str] = None


class StatusResponse(BaseModel):
    online: bool
    cpu_percent: float
    ram_percent: float
    disk_percent: float
    battery_percent: Optional[float]
    network_online: bool
    active_tasks: int
    tools_available: int


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    DONE = "done"
    CANCELLED = "cancelled"
    ERROR = "error"


class TaskStep(BaseModel):
    description: str
    done: bool = False


class Task(BaseModel):
    id: str
    title: str
    steps: List[TaskStep] = Field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    progress: float = 0.0
    result: Optional[Any] = None


class TaskCreateRequest(BaseModel):
    title: str
    steps: List[str] = Field(default_factory=list)


class MemoryEntry(BaseModel):
    key: str
    value: Any

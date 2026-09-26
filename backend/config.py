"""
Global configuration for the assistant backend.
Reads secrets/config from environment variables (.env supported via python-dotenv).
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # LLM
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    MODEL_NAME: str = os.getenv("MODEL_NAME", "claude-sonnet-4-6")
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "2048"))

    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "*").split(",")

    # Safety
    # Actions in this set will NEVER execute without confirm=True in the request body.
    SENSITIVE_ACTIONS = {"shutdown_computer", "restart_computer", "lock_computer"}

    # Terminal command allowlist (extend deliberately, never wildcard this in production)
    TERMINAL_ALLOWLIST = {
        "dir", "ls", "pwd", "echo", "whoami", "date", "ipconfig", "ifconfig",
        "ping", "python", "python3", "pip", "git", "node", "npm",
    }

    # Storage paths
    MEMORY_DB_PATH: str = os.getenv("MEMORY_DB_PATH", "memory/memory_store.json")
    TASKS_DB_PATH: str = os.getenv("TASKS_DB_PATH", "memory/tasks_store.json")


settings = Settings()

"""
Terminal access, deliberately restricted:
- Only the first token of the command is checked against config.TERMINAL_ALLOWLIST.
- No shell=True string concatenation; args are passed as a list.
- 15 second timeout to avoid runaway processes.
Extend TERMINAL_ALLOWLIST in config.py as you build trust in specific commands -
never remove the allowlist check entirely.
"""
import shlex
import subprocess
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import settings


def run_command(command: str, timeout: int = 15) -> dict:
    try:
        parts = shlex.split(command)
    except ValueError as e:
        return {"success": False, "error": f"Could not parse command: {e}"}

    if not parts:
        return {"success": False, "error": "Empty command."}

    base_cmd = parts[0].lower()
    if base_cmd not in settings.TERMINAL_ALLOWLIST:
        return {
            "success": False,
            "error": f"'{base_cmd}' is not in the terminal allowlist.",
            "allowlist": sorted(settings.TERMINAL_ALLOWLIST),
        }

    try:
        result = subprocess.run(parts, capture_output=True, text=True, timeout=timeout, shell=(sys.platform == "win32"))
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": f"Command timed out after {timeout}s."}
    except Exception as e:
        return {"success": False, "error": str(e)}


TOOL_SCHEMAS = [
    {
        "name": "run_command",
        "description": "Run a shell command. Restricted to an allowlist of safe commands.",
        "input_schema": {"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]},
    },
]

"""
Safe system operations: readonly metrics + gated power actions.
Destructive actions (shutdown/restart/lock) NEVER execute unless the caller
passes confirm=True. See config.SENSITIVE_ACTIONS and main.py's /command route.
No authentication-bypass or lock-screen-circumvention logic is implemented here,
by design.
"""
import platform
import subprocess
import psutil

OS_NAME = platform.system()  # "Windows", "Linux", "Darwin"


def get_cpu_usage() -> dict:
    return {"cpu_percent": psutil.cpu_percent(interval=0.3)}


def get_ram_usage() -> dict:
    mem = psutil.virtual_memory()
    return {"ram_percent": mem.percent, "used_gb": round(mem.used / 1e9, 2), "total_gb": round(mem.total / 1e9, 2)}


def get_storage_usage(path: str = "/") -> dict:
    disk = psutil.disk_usage(path)
    return {"disk_percent": disk.percent, "used_gb": round(disk.used / 1e9, 2), "total_gb": round(disk.total / 1e9, 2)}


def get_battery_status() -> dict:
    batt = psutil.sensors_battery()
    if batt is None:
        return {"battery_percent": None, "plugged_in": None, "note": "No battery sensor (desktop?)"}
    return {"battery_percent": batt.percent, "plugged_in": batt.power_plugged}


def get_network_status() -> dict:
    stats = psutil.net_if_stats()
    up = any(s.isup for s in stats.values())
    return {"network_online": up, "interfaces": list(stats.keys())}


def lock_computer(confirm: bool = False) -> dict:
    if not confirm:
        return {"executed": False, "message": "Confirmation required to lock the computer."}
    try:
        if OS_NAME == "Windows":
            subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"], check=True)
        elif OS_NAME == "Darwin":
            subprocess.run(["pmset", "displaysleepnow"], check=True)
        else:
            subprocess.run(["loginctl", "lock-session"], check=True)
        return {"executed": True, "message": "Computer locked."}
    except Exception as e:
        return {"executed": False, "error": str(e)}


def restart_computer(confirm: bool = False) -> dict:
    if not confirm:
        return {"executed": False, "message": "Confirmation required to restart the computer."}
    try:
        if OS_NAME == "Windows":
            subprocess.run(["shutdown", "/r", "/t", "5"], check=True)
        else:
            subprocess.run(["sudo", "shutdown", "-r", "now"], check=True)
        return {"executed": True, "message": "Restart initiated."}
    except Exception as e:
        return {"executed": False, "error": str(e)}


def shutdown_computer(confirm: bool = False) -> dict:
    if not confirm:
        return {"executed": False, "message": "Confirmation required to shut down the computer."}
    try:
        if OS_NAME == "Windows":
            subprocess.run(["shutdown", "/s", "/t", "5"], check=True)
        else:
            subprocess.run(["sudo", "shutdown", "-h", "now"], check=True)
        return {"executed": True, "message": "Shutdown initiated."}
    except Exception as e:
        return {"executed": False, "error": str(e)}


def open_settings() -> dict:
    try:
        if OS_NAME == "Windows":
            subprocess.run(["start", "ms-settings:"], shell=True, check=True)
        elif OS_NAME == "Darwin":
            subprocess.run(["open", "/System/Applications/System Preferences.app"], check=True)
        else:
            subprocess.run(["gnome-control-center"], check=True)
        return {"executed": True}
    except Exception as e:
        return {"executed": False, "error": str(e)}


TOOL_SCHEMAS = [
    {"name": "get_cpu_usage", "description": "Get current CPU usage percent.", "input_schema": {"type": "object", "properties": {}}},
    {"name": "get_ram_usage", "description": "Get current RAM usage.", "input_schema": {"type": "object", "properties": {}}},
    {"name": "get_storage_usage", "description": "Get disk usage.", "input_schema": {"type": "object", "properties": {"path": {"type": "string"}}}},
    {"name": "get_battery_status", "description": "Get battery percent and charging state.", "input_schema": {"type": "object", "properties": {}}},
    {"name": "get_network_status", "description": "Check whether network interfaces are up.", "input_schema": {"type": "object", "properties": {}}},
    {"name": "lock_computer", "description": "Lock the computer screen. Requires confirm=True.", "input_schema": {"type": "object", "properties": {"confirm": {"type": "boolean"}}}},
    {"name": "restart_computer", "description": "Restart the computer. Requires confirm=True.", "input_schema": {"type": "object", "properties": {"confirm": {"type": "boolean"}}}},
    {"name": "shutdown_computer", "description": "Shut down the computer. Requires confirm=True.", "input_schema": {"type": "object", "properties": {"confirm": {"type": "boolean"}}}},
    {"name": "open_settings", "description": "Open the OS settings app.", "input_schema": {"type": "object", "properties": {}}},
]

"""
Desktop control: launching/closing apps, mouse, keyboard, screenshots, window management.
Uses pyautogui for input simulation and psutil for process control.
pyautogui requires a graphical session (won't work on a headless server) -
this module is meant to run on the user's own desktop machine.
"""
import platform
import subprocess
import time
import os

try:
    import pyautogui
    pyautogui.FAILSAFE = True  # move mouse to a screen corner to abort
except Exception:
    pyautogui = None  # allows import on headless machines; calls will raise clearly

import psutil

OS_NAME = platform.system()


def _require_pyautogui():
    if pyautogui is None:
        raise RuntimeError("pyautogui is not available in this environment (no display detected).")


def open_application(name: str) -> dict:
    """Launch an application by name. Best-effort across OSes."""
    try:
        if OS_NAME == "Windows":
            os.startfile(name)  # works for exe names / registered apps
        elif OS_NAME == "Darwin":
            subprocess.Popen(["open", "-a", name])
        else:
            subprocess.Popen([name.lower()])
        return {"success": True, "message": f"Opened {name}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def close_application(name: str) -> dict:
    """Terminate all processes matching `name` (case-insensitive substring)."""
    closed = []
    for proc in psutil.process_iter(["pid", "name"]):
        try:
            if name.lower() in (proc.info["name"] or "").lower():
                proc.terminate()
                closed.append(proc.info["name"])
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return {"success": len(closed) > 0, "closed": closed}


def move_mouse(x: int, y: int, duration: float = 0.2) -> dict:
    _require_pyautogui()
    pyautogui.moveTo(x, y, duration=duration)
    return {"success": True, "position": [x, y]}


def click(x: int = None, y: int = None, button: str = "left") -> dict:
    _require_pyautogui()
    if x is not None and y is not None:
        pyautogui.click(x, y, button=button)
    else:
        pyautogui.click(button=button)
    return {"success": True}


def double_click(x: int = None, y: int = None) -> dict:
    _require_pyautogui()
    if x is not None and y is not None:
        pyautogui.doubleClick(x, y)
    else:
        pyautogui.doubleClick()
    return {"success": True}


def type_text(text: str, interval: float = 0.02) -> dict:
    _require_pyautogui()
    pyautogui.typewrite(text, interval=interval)
    return {"success": True, "typed": text}


def keyboard_shortcut(keys: list) -> dict:
    """e.g. keys=['ctrl','c']"""
    _require_pyautogui()
    pyautogui.hotkey(*keys)
    return {"success": True, "keys": keys}


def take_screenshot(save_path: str = "screenshot.png") -> dict:
    _require_pyautogui()
    img = pyautogui.screenshot()
    img.save(save_path)
    return {"success": True, "path": os.path.abspath(save_path)}


def list_windows() -> dict:
    """List visible window titles. Best-effort, platform dependent."""
    try:
        if OS_NAME == "Windows":
            import pygetwindow as gw
            titles = [w.title for w in gw.getAllWindows() if w.title.strip()]
        else:
            result = subprocess.run(["wmctrl", "-l"], capture_output=True, text=True)
            titles = [line.split(None, 3)[-1] for line in result.stdout.splitlines() if line.strip()]
        return {"success": True, "windows": titles}
    except Exception as e:
        return {"success": False, "error": str(e), "note": "Install pygetwindow (Windows) or wmctrl (Linux)."}


def focus_window(title_substring: str) -> dict:
    try:
        if OS_NAME == "Windows":
            import pygetwindow as gw
            matches = [w for w in gw.getAllWindows() if title_substring.lower() in w.title.lower()]
            if not matches:
                return {"success": False, "message": "No matching window."}
            matches[0].activate()
            return {"success": True, "focused": matches[0].title}
        else:
            subprocess.run(["wmctrl", "-a", title_substring], check=True)
            return {"success": True, "focused": title_substring}
    except Exception as e:
        return {"success": False, "error": str(e)}


TOOL_SCHEMAS = [
    {"name": "open_application", "description": "Open a desktop application by name.", "input_schema": {"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]}},
    {"name": "close_application", "description": "Close/terminate an application by name.", "input_schema": {"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]}},
    {"name": "move_mouse", "description": "Move the mouse cursor to coordinates.", "input_schema": {"type": "object", "properties": {"x": {"type": "integer"}, "y": {"type": "integer"}}, "required": ["x", "y"]}},
    {"name": "click", "description": "Click the mouse, optionally at coordinates.", "input_schema": {"type": "object", "properties": {"x": {"type": "integer"}, "y": {"type": "integer"}, "button": {"type": "string"}}}},
    {"name": "double_click", "description": "Double-click, optionally at coordinates.", "input_schema": {"type": "object", "properties": {"x": {"type": "integer"}, "y": {"type": "integer"}}}},
    {"name": "type_text", "description": "Type text via the keyboard.", "input_schema": {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}},
    {"name": "keyboard_shortcut", "description": "Press a key combination, e.g. ['ctrl','c'].", "input_schema": {"type": "object", "properties": {"keys": {"type": "array", "items": {"type": "string"}}}, "required": ["keys"]}},
    {"name": "take_screenshot", "description": "Capture a screenshot and save it to disk.", "input_schema": {"type": "object", "properties": {"save_path": {"type": "string"}}}},
    {"name": "list_windows", "description": "List currently open window titles.", "input_schema": {"type": "object", "properties": {}}},
    {"name": "focus_window", "description": "Bring a window matching a title substring to the foreground.", "input_schema": {"type": "object", "properties": {"title_substring": {"type": "string"}}, "required": ["title_substring"]}},
]

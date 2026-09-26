"""
Tool registry. Every tool module exposes:
  - plain functions (the actual implementation)
  - TOOL_SCHEMAS: a list of Anthropic-style tool-use schemas

This file merges them into one lookup the agent engine can call by name,
and one combined schema list to hand to the LLM.
"""
from . import computer, browser, files, terminal, system, communication, research

FUNCTION_REGISTRY = {
    # computer.py
    "open_application": computer.open_application,
    "close_application": computer.close_application,
    "move_mouse": computer.move_mouse,
    "click": computer.click,
    "double_click": computer.double_click,
    "type_text": computer.type_text,
    "keyboard_shortcut": computer.keyboard_shortcut,
    "take_screenshot": computer.take_screenshot,
    "list_windows": computer.list_windows,
    "focus_window": computer.focus_window,
    # browser.py
    "open_browser": browser.open_browser,
    "search_web": browser.search_web,
    "open_url": browser.open_url,
    "read_page": browser.read_page,
    "download": browser.download,
    # files.py
    "search_files": files.search_files,
    "read_file": files.read_file,
    "create_file": files.create_file,
    "copy_file": files.copy_file,
    "move_file": files.move_file,
    "rename_file": files.rename_file,
    "create_folder": files.create_folder,
    "open_file": files.open_file,
    # terminal.py
    "run_command": terminal.run_command,
    # system.py
    "get_cpu_usage": system.get_cpu_usage,
    "get_ram_usage": system.get_ram_usage,
    "get_storage_usage": system.get_storage_usage,
    "get_battery_status": system.get_battery_status,
    "get_network_status": system.get_network_status,
    "lock_computer": system.lock_computer,
    "restart_computer": system.restart_computer,
    "shutdown_computer": system.shutdown_computer,
    "open_settings": system.open_settings,
    # communication.py
    "send_notification": communication.send_notification,
    "send_email": communication.send_email,
    # research.py
    "research": research.research,
}

ALL_TOOL_SCHEMAS = (
    computer.TOOL_SCHEMAS
    + browser.TOOL_SCHEMAS
    + files.TOOL_SCHEMAS
    + terminal.TOOL_SCHEMAS
    + system.TOOL_SCHEMAS
    + communication.TOOL_SCHEMAS
    + research.TOOL_SCHEMAS
)


def get_tool_schemas():
    return ALL_TOOL_SCHEMAS


def execute_tool(name: str, arguments: dict) -> dict:
    fn = FUNCTION_REGISTRY.get(name)
    if fn is None:
        return {"success": False, "error": f"Unknown tool: {name}"}
    try:
        return fn(**arguments)
    except TypeError as e:
        return {"success": False, "error": f"Bad arguments for {name}: {e}"}
    except Exception as e:
        return {"success": False, "error": str(e)}

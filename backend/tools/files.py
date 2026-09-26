"""
File management: search, read, create, copy, move, rename, open.
Text extraction supported for: TXT, PDF, DOCX, XLSX, PPTX, CSV, images (metadata only).
"""
import os
import shutil
import platform
import subprocess
from pathlib import Path

OS_NAME = platform.system()


def search_files(query: str, root: str = None, max_results: int = 25) -> dict:
    root = root or str(Path.home())
    matches = []
    for dirpath, _, filenames in os.walk(root):
        for fname in filenames:
            if query.lower() in fname.lower():
                matches.append(os.path.join(dirpath, fname))
                if len(matches) >= max_results:
                    return {"success": True, "matches": matches}
    return {"success": True, "matches": matches}


def read_file(path: str) -> dict:
    ext = Path(path).suffix.lower()
    try:
        if ext == ".txt" or ext == ".csv":
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                return {"success": True, "content": f.read()}
        elif ext == ".pdf":
            from pypdf import PdfReader
            reader = PdfReader(path)
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
            return {"success": True, "content": text}
        elif ext == ".docx":
            import docx
            doc = docx.Document(path)
            text = "\n".join(p.text for p in doc.paragraphs)
            return {"success": True, "content": text}
        elif ext == ".xlsx":
            import openpyxl
            wb = openpyxl.load_workbook(path, data_only=True)
            sheets = {}
            for ws in wb.worksheets:
                sheets[ws.title] = [[c.value for c in row] for row in ws.iter_rows()]
            return {"success": True, "content": sheets}
        elif ext == ".pptx":
            from pptx import Presentation
            prs = Presentation(path)
            slides_text = []
            for slide in prs.slides:
                texts = [shape.text for shape in slide.shapes if shape.has_text_frame]
                slides_text.append("\n".join(texts))
            return {"success": True, "content": slides_text}
        elif ext in (".png", ".jpg", ".jpeg", ".gif", ".webp"):
            return {"success": True, "content": None, "note": "Image file - use a vision-capable LLM call to interpret it.", "path": path}
        else:
            return {"success": False, "error": f"Unsupported file type: {ext}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def create_file(path: str, content: str = "") -> dict:
    try:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return {"success": True, "path": os.path.abspath(path)}
    except Exception as e:
        return {"success": False, "error": str(e)}


def copy_file(src: str, dst: str) -> dict:
    try:
        shutil.copy2(src, dst)
        return {"success": True, "dst": dst}
    except Exception as e:
        return {"success": False, "error": str(e)}


def move_file(src: str, dst: str) -> dict:
    try:
        shutil.move(src, dst)
        return {"success": True, "dst": dst}
    except Exception as e:
        return {"success": False, "error": str(e)}


def rename_file(src: str, new_name: str) -> dict:
    try:
        new_path = os.path.join(os.path.dirname(src), new_name)
        os.rename(src, new_path)
        return {"success": True, "new_path": new_path}
    except Exception as e:
        return {"success": False, "error": str(e)}


def create_folder(path: str) -> dict:
    try:
        os.makedirs(path, exist_ok=True)
        return {"success": True, "path": os.path.abspath(path)}
    except Exception as e:
        return {"success": False, "error": str(e)}


def open_file(path: str) -> dict:
    try:
        if OS_NAME == "Windows":
            os.startfile(path)
        elif OS_NAME == "Darwin":
            subprocess.run(["open", path], check=True)
        else:
            subprocess.run(["xdg-open", path], check=True)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


TOOL_SCHEMAS = [
    {"name": "search_files", "description": "Search for files by name under a root directory.", "input_schema": {"type": "object", "properties": {"query": {"type": "string"}, "root": {"type": "string"}}, "required": ["query"]}},
    {"name": "read_file", "description": "Read text content from txt/pdf/docx/xlsx/pptx/csv files.", "input_schema": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}},
    {"name": "create_file", "description": "Create a new text file with optional content.", "input_schema": {"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}}, "required": ["path"]}},
    {"name": "copy_file", "description": "Copy a file to a destination.", "input_schema": {"type": "object", "properties": {"src": {"type": "string"}, "dst": {"type": "string"}}, "required": ["src", "dst"]}},
    {"name": "move_file", "description": "Move a file to a destination.", "input_schema": {"type": "object", "properties": {"src": {"type": "string"}, "dst": {"type": "string"}}, "required": ["src", "dst"]}},
    {"name": "rename_file", "description": "Rename a file in place.", "input_schema": {"type": "object", "properties": {"src": {"type": "string"}, "new_name": {"type": "string"}}, "required": ["src", "new_name"]}},
    {"name": "create_folder", "description": "Create a new folder (including parents).", "input_schema": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}},
    {"name": "open_file", "description": "Open a file with its default application.", "input_schema": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}},
]

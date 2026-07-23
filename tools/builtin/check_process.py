import json
import os
from datetime import datetime
from pathlib import Path
import time

SCHEMA = {
    "type": "function",
    "function": {
        "name": "check_process",
        "description": (
            "Check the status and recent output of a background process "
            "started with run_background."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "process_id": {
                    "type": "string",
                    "description": "The process id returned by run_background (e.g. 'proc_1784752442')",
                }
            },
            "required": ["process_id"],
        },
    },
}


def _is_running(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False
    except Exception:
        return False


def run(process_id: str) -> str:
    proc_dir = Path.cwd() / ".pedalo" / "processes"
    meta_path = proc_dir / f"{process_id}.json"
    log_path = proc_dir / f"{process_id}.log"

    if not meta_path.exists():
        return f"Error: unknown process '{process_id}'."

    meta = json.loads(meta_path.read_text(encoding="utf-8"))

    if meta["finished_at"] is not None:
        status = f"finished (at {meta['finished_at']})"
    elif _is_running(meta["pid"]):
        status = "running"
    else:
        recently_active = False
        if log_path.exists():
            age = time.time() - log_path.stat().st_mtime
            recently_active = age < 10
        if recently_active:
            status = "probably running (log still being written)"
        else:
            meta["finished_at"] = datetime.now().isoformat()
            meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
            status = f"finished (detected now, at {meta['finished_at']})"

    if log_path.exists():
        raw = log_path.read_bytes()
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            text = raw.decode("cp850", errors="replace")
        lines = text.splitlines()
        tail = "\n".join(lines[-30:])
    else:
        tail = "(no log output)"

    if "running" in status:
        advice = (
            "\n\nThe process is still running. Do NOT call check_process again now. "
            "Report the current status to the user and end your turn. "
            "The user monitors the process in the UI and will ask you to check again if needed."
        )
    else:
        advice = ""

    return (
        f"Process {process_id}: {status}\n"
        f"Command: {meta['command']}\n"
        f"--- last output ---\n{tail}{advice}"
    )
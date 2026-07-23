import json
import os
from datetime import datetime
from pathlib import Path

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
        meta["finished_at"] = datetime.now().isoformat()
        meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
        status = f"finished (detected now, at {meta['finished_at']})"

    if log_path.exists():
        lines = log_path.read_text(encoding="utf-8", errors="replace").splitlines()
        tail = "\n".join(lines[-30:])
    else:
        tail = "(no log output)"

    return (
        f"Process {process_id}: {status}\n"
        f"Command: {meta['command']}\n"
        f"--- last output ---\n{tail}"
    )
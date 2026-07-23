import json
import platform
import subprocess
import time
from datetime import datetime
from pathlib import Path

SCHEMA = {
    "type": "function",
    "function": {
        "name": "run_background",
        "description": (
            "Launch a long-running command (training, server...) in the background. "
            "Returns a process id immediately without waiting for completion. "
            "Use check_process to monitor its status and output."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The shell command to run in the background",
                },
            },
            "required": ["command"],
        },
    },
}

REQUIRES_CONFIRMATION = True


def run(command: str) -> str:
    proc_dir = Path.cwd() / ".pedalo" / "processes"
    proc_dir.mkdir(parents=True, exist_ok=True)

    proc_id = f"proc_{int(time.time())}"
    log_path = proc_dir / f"{proc_id}.log"
    meta_path = proc_dir / f"{proc_id}.json"

    try:
        log_file = open(log_path, "w", encoding="utf-8")

        popen_kwargs = {
            "stdout": log_file,
            "stderr": subprocess.STDOUT,
            "stdin": subprocess.DEVNULL,
            "text": True,
            "cwd": Path.cwd(),
        }

        if platform.system() == "Windows":
            popen_kwargs["creationflags"] = (
                subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.CREATE_NO_WINDOW
            )
            cmd = ["cmd", "/c", f"chcp 65001>nul & {command}"]
        else:
            popen_kwargs["start_new_session"] = True
            cmd = ["bash", "-c", command]

        process = subprocess.Popen(cmd, **popen_kwargs)
    except Exception as e:
        return f"Error: could not start command: {e}"

    meta = {
        "id": proc_id,
        "command": command,
        "pid": process.pid,
        "log_path": str(log_path),
        "started_at": datetime.now().isoformat(),
        "finished_at": None,
        "exit_code": None,
    }
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")

    return (
        f"Started {proc_id} (pid {process.pid}). Running in background. "
        f"Use check_process('{proc_id}') to monitor its status and output."
    )
import re
import subprocess
import platform

IS_WINDOWS = platform.system() == "Windows"

SCHEMA = {
    "type": "function",
    "function": {
        "name": "bash",
        "description": (
            f"Execute a shell command ({'PowerShell' if IS_WINDOWS else 'bash'} syntax, "
            f"{platform.system()}). Returns stdout, stderr and exit code. "
            "The user must approve each command before it runs."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": f"The shell command to run ({'PowerShell' if IS_WINDOWS else 'bash'} syntax)"
                }
            },
            "required": ["command"]
        }
    }
}

REQUIRES_CONFIRMATION = True

MAX_OUTPUT = 4000

BLOCKED_PATTERNS = [
    r"\brm\s+-\w*r\w*\s+[/\\]",
    r"\bformat\b",
    r"\bdiskpart\b",
    r"\bshutdown\b",
    r"\bmkfs\b",
]


def run(command: str) -> str:
    for pattern in BLOCKED_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            return "Error: command blocked by safety policy. It was not executed."

    if IS_WINDOWS:
        wrapped = f"[Console]::OutputEncoding = [System.Text.Encoding]::UTF8; {command}"
        cmd = ["powershell", "-NoProfile", "-Command", wrapped]
    else:
        cmd = ["bash", "-c", command]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=60,
        )
    except subprocess.TimeoutExpired:
        return "Error: command timed out after 60 seconds."
    except Exception as e:
        return f"Error: could not execute command: {e}"

    parts = []
    if result.stdout.strip():
        parts.append(result.stdout.strip())
    if result.stderr.strip():
        parts.append(f"STDERR:\n{result.stderr.strip()}")
    if result.returncode != 0:
        parts.append(f"Exit code: {result.returncode}")

    output = "\n\n".join(parts) if parts else "(no output, exit code 0)"

    if len(output) > MAX_OUTPUT:
        omitted = len(output) - MAX_OUTPUT
        output = f"{output[:MAX_OUTPUT]}\n\n[Truncated {omitted} characters]"

    return output
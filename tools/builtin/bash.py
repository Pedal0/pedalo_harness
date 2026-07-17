import re
import subprocess

SCHEMA = {
    "type": "function",
    "function": {
        "name": "bash",
        "description": (
            "Execute a shell command on Windows (PowerShell syntax). "
            "Returns stdout, stderr and exit code. "
            "The user must approve each command before it runs."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The shell command to run (PowerShell syntax)"
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

    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", command],
            capture_output=True,
            text=True,
            timeout=60,
            encoding="utf-8",
            errors="replace"
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
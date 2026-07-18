from pathlib import Path

SCHEMA = {
    "type": "function",
    "function": {
        "name": "read_file",
        "description": (
            "Read a text file. For large files, read in chunks using offset and limit, "
            "and continue with the offset suggested at the end of the result."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path of the file to read"
                },
                "offset": {
                    "type": "integer",
                    "description": "Line number to start reading from (0-indexed). Optional, default 0."
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of lines to read. Optional, default 500."
                }
            },
            "required": ["path"]
        }
    }
}

MAX_CHARS = 4000


def run(path: str, offset: int = 0, limit: int = 500) -> str:
    file = Path(path)
    if not file.exists():
        return f"Error: the file {file} does not exist"

    with file.open("rb") as f:
        sample = f.read(1024)
    if b"\x00" in sample:
        return f"Error: {file} is a binary file and cannot be read as text."

    try:
        all_lines = file.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        return f"Error: {file} is not valid UTF-8 text. It may be binary or use another encoding."

    total = len(all_lines)

    if offset >= total:
        return f"Error: offset {offset} is beyond the end of the file ({total} lines)"

    chunk_lines = all_lines[offset:offset + limit]
    content = "\n".join(chunk_lines)

    if len(content) > MAX_CHARS:
        omitted = len(content) - MAX_CHARS
        content = f"{content[:MAX_CHARS]}\n\n[Truncated {omitted} characters within this chunk]"

    end = offset + len(chunk_lines)
    if end < total:
        content += f"\n\n[Showing lines {offset}-{end} of {total}. Use offset={end} to continue.]"

    return content
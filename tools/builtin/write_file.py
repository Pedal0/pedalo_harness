from pathlib import Path

SCHEMA = {
    "type": "function",
    "function": {
        "name": "write_file",
        "description": "Write content to a file, creating it if needed (overwrites existing content)",
        "parameters": {
            "type": "object",
            "properties": {
                "path":{
                    "type": "string",
                    "description": "Path of the file to write"
                },
                "content":{
                    "type": "string",
                    "description": "Content to write to the file"
                }
            },
            "required": ["path", "content"]
        }
    }
}

def run(path: str, content: str) -> str:
    file = Path(path)
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text(content, encoding="utf-8")
    return f"Wrote {len(content)} characters to {file}"


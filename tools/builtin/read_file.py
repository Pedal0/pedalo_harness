from pathlib import Path

SCHEMA = {
    "type": "function",
    "function": {
        "name": "read_file",
        "description": "Read a file to get the content",
        "parameters": {
            "type": "object",
            "properties": {
                "path":{
                    "type": "string",
                    "description": "Path of the file to read"
                }
            },
            "required": ["path"]
        }
    }
}

def run(path: str) -> str:
    file = Path(path)
    if not file.exists():
        return f"Error the file {file} does not exist"
    
    content = file.read_text(encoding="utf-8")
    file_size = len(content)

    if file_size > 4000:
        count_truncate = file_size - 4000
        content = f"{content[:4000]} \n\n[Truncated {count_truncate} characters]"

    return content

from pathlib import Path

SCHEMA = {
    "type": "function",
    "function": {
        "name": "edit_file",
        "description": "Edit a file by replacing a specific string",
        "parameters": {
            "type": "object",
            "properties": {
                "path":{
                    "type": "string",
                    "description": "Path of the file to edit"
                },
                "old_str":{
                    "type": "string",
                    "description": "String to replace in the file"
                },
                "new_str":{
                    "type": "string",
                    "description": "New string to replace the old string in the file"
                }
            },
            "required": ["path", "old_str", "new_str"]
        }
    }
}

REQUIRES_CONFIRMATION = True

def run(path: str, old_str: str, new_str: str) -> str:
    file = Path(path)

    if not file.exists():
        return f"Error: the file {file} does not exist"
    if old_str == new_str:
        return f"Error: old_str and new_str are identical, no changes made"

    content = file.read_text(encoding="utf-8")

    count = content.count(old_str)
    if count == 0:
        return f"Error: the string was not found in {file}. Re-read the file with read_file, your version may be outdated"
    if count > 1:
        return f"Error: the string was found {count} times in {file}. Add surrounding lines to old_str to make it unique"

    lines_before = len(content.splitlines())
    content = content.replace(old_str, new_str)
    file.write_text(content, encoding="utf-8")
    lines_after = len(content.splitlines())

    return f"Successfully edited {file}: {lines_before} -> {lines_after} lines"
from pathlib import Path

EXCLUDED = {
    "venv", ".venv", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache",
    ".tox",
    "node_modules", ".next", ".nuxt", ".svelte-kit", "dist", "build", "out",
    ".turbo", ".parcel-cache", ".vite", "coverage",
    ".git", ".idea", ".vscode", ".DS_Store",
    ".env", ".env.local", ".env.production", ".env.development",
    "target",                   
    ".gradle", "bin", "obj",    
    ".pedalo",
}

EXCLUDED_SUFFIXES = (".egg-info",)

BINARY_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".ico", ".svg",
                     ".mp4", ".mov", ".webm", ".mp3", ".wav",
                     ".pdf", ".zip", ".woff", ".woff2", ".ttf", ".eot"}

LARGE_FILE_THRESHOLD = 100 * 1024   # 100 KB
MAX_MAP_ENTRIES = 500

TEMPLATES = {
    "decisions.md": "# Decisions\n\nArchitectural and design decisions made on this project.\n",
    "lessons.md": "# Lessons\n\nProblems encountered and what solved them. One line per lesson.\n",
    "state.md": "# State\n\nCurrent task, progress, and next steps.\n",
}


def _is_excluded(path: Path) -> bool:
    for part in path.parts:
        if part in EXCLUDED:
            return True
        if part.endswith(EXCLUDED_SUFFIXES):
            return True
    return False


def generate_map(project_root: Path) -> str:
    lines = [
        "# Project Map",
        "",
        "Auto-generated skeleton. Add a one-line description after any file",
        "you have explored, using edit_file (append ' — description' to the line).",
        "",
    ]

    by_folder: dict[str, list[str]] = {}
    for path in sorted(project_root.rglob("*")):
        if not path.is_file():
            continue
        if _is_excluded(path):
            continue

        relative = path.relative_to(project_root)
        folder = str(relative.parent)
        size = path.stat().st_size
        size_kb = size / 1024

        if path.suffix.lower() in BINARY_EXTENSIONS:
            entry = f"- {relative.name} ({size_kb:.0f} KB) [binary]"
        elif size > LARGE_FILE_THRESHOLD:
            entry = f"- {relative.name} ({size_kb:.0f} KB) ⚠️ large — read in chunks"
        else:
            entry = f"- {relative.name} ({size_kb:.1f} KB)"
        by_folder.setdefault(folder, []).append(entry)

    total_files = sum(len(v) for v in by_folder.values())
    if total_files > MAX_MAP_ENTRIES:
        lines.append(
            f"⚠️ Project has {total_files} files — map truncated to a folders overview. "
            "Some build/cache folders may need to be excluded."
        )
        lines.append("")
        for folder in sorted(by_folder):
            title = "(root)" if folder == "." else folder
            lines.append(f"- {title}/ ({len(by_folder[folder])} files)")
        return "\n".join(lines)

    for folder, entries in sorted(by_folder.items()):
        title = "(root)" if folder == "." else folder
        lines.append(f"## {title}")
        lines.extend(entries)
        lines.append("")

    return "\n".join(lines)


def ensure_brain(project_root: Path) -> Path:
    """Create .pedalo/ and its files if missing. Never overwrites. Returns the brain path."""
    brain_dir = project_root / ".pedalo"
    brain_dir.mkdir(exist_ok=True)

    map_file = brain_dir / "MAP.md"
    if not map_file.exists():
        map_file.write_text(generate_map(project_root), encoding="utf-8")

    for filename, template in TEMPLATES.items():
        file = brain_dir / filename
        if not file.exists():
            file.write_text(template, encoding="utf-8")

    return brain_dir
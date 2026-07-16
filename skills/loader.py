from pathlib import Path

SKILLS_DIR = Path(__file__).parent / "library"


def load_skills() -> list[dict]:
    skills = []

    for folder in SKILLS_DIR.iterdir():
        if not folder.is_dir():
            continue

        skill_file = folder / "SKILL.md"

        if not skill_file.exists():
            print(f"Warning: {skill_file} does not exist, skipping.")
            continue

        content = skill_file.read_text(encoding="utf-8")

        if not content.startswith("---"):
            print(f"Warning: {skill_file} does not start with '---', skipping.")
            continue

        frontmatter = content.split("---", 2)[1]

        meta = {}
        for line in frontmatter.splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                meta[key.strip()] = value.strip()
        
        if not meta.get("name") or not meta.get("description"):
            print(f"Warning: {skill_file} is missing 'name' or 'description', skipping.")
            continue

        skills.append({
            "name": meta["name"],
            "description": meta["description"],
            "path": str(skill_file),
        })

    return skills


def format_skills_prompt(skills: list[dict]) -> str:
    if not skills:
        return ""

    lines = [
        "",
        "# Skills available",
        "",
        "Before using a skill, please read its documentation in the SKILL.md file with read_file.",
        "",
    ]
    for skill in skills:
        lines.append(f"- {skill['name']} ({skill['path']}) : {skill['description']}")

    return "\n".join(lines)
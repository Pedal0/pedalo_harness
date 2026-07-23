# Pedalo Local Coding Harness

**Pedalo** is a lightweight terminal AI coding agent that runs entirely against your local [Ollama](https://ollama.com) models. It reads, writes and edits files, runs shell commands, and remembers your project between sessions no cloud, no API keys, no subscription.

![Platform](https://img.shields.io/badge/platform-cross--platform-blue)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![Backend](https://img.shields.io/badge/backend-Ollama-orange)

---

## Overview

Pedalo is a small agent loop wrapped in a [Textual](https://github.com/Textualize/textual) terminal UI (the ⛵ "lake" animates while the agent works). It talks to a model served by Ollama on your machine, gives it a set of tools to act on your project, and keeps a per-project memory so it doesn't start from zero every time.

**Key capabilities:**

- **Terminal UI** animated activity indicator, collapsible tool calls, running background processes, live model switcher
- **Built-in tools** `read_file`, `write_file`, `edit_file`, `bash`, `run_background`, `check_process`
- **Skills** drop a `SKILL.md` in `skills/library/` and the agent can discover and use it
- **Project brain** auto-generates a project map plus `decisions.md`, `lessons.md`, `state.md` in `.pedalo/` so context survives between sessions
- **Offline** everything runs through your local Ollama server, nothing leaves your machine
- **Copy to clipboard** `/copy` grabs the whole session as markdown

---

## Requirements

| Component | Minimum |
|---|---|
| OS | Windows / macOS / Linux |
| Python | 3.11+ |
| [Ollama](https://ollama.com) | installed and running (`ollama serve`) |
| A tool-calling model | pulled locally (e.g. `ollama pull qwen2.5-coder`) |

---

## Setup

### 1. Clone the repository

```bash
git clone <repo-url>
cd harness
```

### 2. Install dependencies

```bash
pip install -e .
```

This installs Pedalo and its two dependencies (`requests`, `textual`), and registers the `pedalo` command.

### 3. Point it at a model

Edit [providers/ollama/models.json](providers/ollama/models.json) and set `"default"` to a model you have pulled in Ollama:

```json
{
  "default": "qwen2.5-coder:latest",
  "host": "http://localhost:11434",
  "num_ctx": 120000
}
```

> You can also switch models on the fly from the dropdown at the top of the TUI it lists whatever `ollama list` sees locally.

### 4. Run it

```bash
pedalo
```

Run it from inside the project you want the agent to work on Pedalo uses your current directory as the project root and builds its memory there (`.pedalo/`).

---

## Usage

| Input | Result |
|---|---|
| Type a request and press Enter | Agent plans, calls tools, and replies in the chat |
| `/skill <name> <request>` | Runs your request with a specific skill's instructions loaded |
| `/copy` | Copies the whole session (markdown) to the clipboard |
| `/exit` | Quits |

Tool calls appear as collapsible entries you can expand to see arguments and output. Background commands (started via `run_background`) show up live in the process bar.

---

## Project Structure

```
harness/
├── pedalo.py           # entry point (TUI)
├── main.py             # simple console entry point (no UI)
├── core/                # agent loop
├── providers/            # model backends (Ollama)
│   └── ollama/
│       ├── provider.py
│       └── models.json  # default model / host / context size
├── tools/builtin/        # read_file, write_file, edit_file, bash, run_background, check_process
├── skills/library/       # drop-in skills (SKILL.md per folder)
├── prompts/system/       # system prompt, environment, brain prompts
├── brain/scanner.py      # builds the per-project memory in .pedalo/
└── ui/                   # Textual app (app.py, lake.py, processes.py, confirm.py)
```

---

## License

No license specified personal project.

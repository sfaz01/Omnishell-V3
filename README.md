<div align="center">

# 🧠 OmniShell

**Self-Healing AI Terminal Assistant for Linux**

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Platform](https://img.shields.io/badge/Platform-Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black)](https://kernel.org)
[![AI](https://img.shields.io/badge/AI-Multi--LLM-8B5CF6?style=for-the-badge&logo=openai&logoColor=white)](#-supported-llm-providers)
[![License](https://img.shields.io/badge/License-MIT-22C55E?style=for-the-badge)](LICENSE)

*Describe what you want in plain English → OmniShell generates the right command for your distro, explains it, and auto-fixes itself if anything goes wrong.*

---

</div>

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🧠 **Distro-Agnostic** | Auto-detects your Linux distro (Arch, Ubuntu, Fedora, etc.) and uses the correct package manager |
| 🩹 **Self-Healing** | If a command fails, OmniShell captures the error and suggests a fixed version automatically |
| 🛡️ **Safety First** | Regex-based blocklist prevents dangerous commands (`rm -rf /`, fork bombs, disk overwrites) |
| 👁️ **Context Aware** | Runs diagnostic commands to understand your system state before generating commands |
| 🗣️ **Explain Mode** | Press `x` to get a plain-English explanation of any suggested command |
| 💬 **Conversational** | Remembers context — say "install nginx" then "now start it" and it knows what "it" means |
| 📜 **Command History** | SQLite-backed history with stats — never lose track of what you've run |
| 🎨 **Rich Terminal UI** | Beautiful output with syntax highlighting, panels, spinners, and tables |
| 🌐 **Web Dashboard** | Streamlit-powered web UI with dark glassmorphism theme |
| 🔌 **Multi-LLM** | Works with Groq, Ollama (local), OpenAI, and Google Gemini |
| 🏃 **Dry-Run Mode** | Preview commands without executing — great for learning |

## 🚀 Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/sfaz01/Omnishell-v3.git
cd Omnishell

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install OmniShell
pip install -e .

# Or with all LLM providers + web UI:
pip install -e ".[all]"
```

### 2. Configure

```bash
cp .env.example .env
# Edit .env and add your API key
```

Get a **free** Groq API key at [console.groq.com](https://console.groq.com).

### 3. Run

```bash
# Interactive mode
omni

# Single command
omni "update my system"

# With options
omni --mode newbie --provider groq "install docker"
omni --dry-run "delete old kernels"
```

## 💻 Usage Modes

### CLI Mode (Terminal)

```bash
omni                        # Interactive REPL
omni "your task"            # One-shot mode
omni --mode newbie          # Beginner-friendly (extra explanations)
omni --mode pro             # Default (command-only, safe mode on)
omni --mode god             # No restrictions, auto-execute (⚠️ careful!)
omni --dry-run              # Preview without executing
omni --provider ollama      # Use local Ollama models
```

**In-session commands:**
- `history` — View past commands in a table
- `stats` — See success/failure statistics
- `clear` — Reset conversation memory
- `clear history` — Wipe command history
- `exit` — Quit

### Web Mode (Browser)

```bash
streamlit run omnishell/web.py
```

Features a dark glassmorphism UI with:
- Chat interface for natural language commands
- Sidebar with provider/model/mode configuration
- Real-time stats and command history
- Automatic command explanations

## 🔌 Supported LLM Providers

| Provider | Install | Key Required | Notes |
|----------|---------|:---:|-------|
| **Groq** | Included | `GROQ_API_KEY` | Free tier, fastest inference |
| **Ollama** | `pip install -e ".[ollama]"` | None | Fully local, private |
| **OpenAI** | `pip install -e ".[openai]"` | `OPENAI_API_KEY` | GPT-4o-mini default |
| **Gemini** | `pip install -e ".[gemini]"` | `GOOGLE_API_KEY` | Gemini Flash default |

Switch providers via CLI flag or environment variable:

```bash
# CLI flag
omni --provider ollama "list running containers"

# Environment variable
export OMNISHELL_PROVIDER=gemini
omni "check memory usage"
```

## 📁 Project Structure

```
omnishell/
├── omnishell/
│   ├── __init__.py      # Package metadata
│   ├── core.py          # OS detection, command execution, config
│   ├── prompts.py       # All LLM prompt templates
│   ├── safety.py        # Command blocklist & validation
│   ├── llm.py           # Multi-LLM factory with retry logic
│   ├── history.py       # SQLite command history
│   ├── memory.py        # Conversational context memory
│   ├── cli.py           # Rich-powered terminal interface
│   └── web.py           # Streamlit web dashboard
├── pyproject.toml       # Modern Python packaging
├── .env.example         # Configuration template
├── LICENSE              # MIT License
└── README.md
```

## 🛡️ Safety

OmniShell uses a **multi-layer safety system**:

1. **LLM-Level:** The prompt instructs the AI to output `SAFE_MODE_ERROR` for dangerous requests (pro mode)
2. **Regex Blocklist:** Hard-coded patterns block commands like `rm -rf /`, fork bombs, and disk overwrites regardless of what the LLM outputs
3. **Sudo Warnings:** Commands using `sudo` or destructive operations trigger explicit warnings
4. **User Confirmation:** Every command requires manual approval before execution (except god mode)
5. **Dry-Run Mode:** Preview commands without any execution

## ⚙️ Configuration

All settings can be configured via environment variables in `.env`:

| Variable | Default | Description |
|----------|---------|-------------|
| `GROQ_API_KEY` | — | Groq API key (required for Groq provider) |
| `OMNISHELL_PROVIDER` | `groq` | LLM provider (`groq`, `ollama`, `openai`, `gemini`) |
| `OMNISHELL_MODEL` | Per provider | Override the default model |
| `OPENAI_API_KEY` | — | OpenAI API key |
| `GOOGLE_API_KEY` | — | Google Gemini API key |

## 📄 License

MIT © Sarfaraz

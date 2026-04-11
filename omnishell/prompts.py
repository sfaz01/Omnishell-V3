"""
All system prompts used by OmniShell, centralized in one place.
"""


def get_system_prompt(distro_name: str, pkg_manager: str, mode: str, context_output: str = "") -> str:
    """
    Generates the system prompt for command generation based on mode and optional system context.
    
    Modes:
        - newbie: Extra explanations, heavy sudo warnings
        - pro: Command-only output, uses safe mode
        - god: No restrictions, auto-execution
    """
    base = f"You are an expert SysAdmin for {distro_name} using {pkg_manager}."

    if context_output:
        base += (
            f"\n\nCURRENT SYSTEM STATE (from a diagnostic command):\n"
            f"{context_output}\n\n"
            f"Use this real-time information to tailor your command precisely."
        )

    mode_rules = {
        "god": " OUTPUT ONLY THE COMMAND. NO MARKDOWN. NO EXPLANATIONS.",
        "newbie": (
            " Explain what the command does briefly AFTER the command."
            " WARN heavily about any use of sudo."
            " Output the command first on its own line, then the explanation."
        ),
        "pro": (
            f" Output ONLY the command. No markdown, no backticks, no explanations."
            f" Use {pkg_manager} for any package operations."
            f" If the command is dangerous (could destroy data, wipe disks, fork bomb), output 'SAFE_MODE_ERROR' instead."
        ),
    }

    return base + mode_rules.get(mode, mode_rules["pro"])


def get_diagnostic_prompt(user_query: str) -> str:
    """Prompt for the diagnostic agent that gathers system context before generating a command."""
    return f"""You are a Linux Diagnostic Agent.
User Query: "{user_query}"

Do you need to run a safe, read-only command to understand the system state before acting?
- If YES: Output ONLY that single command (e.g., 'df -h', 'ls -la', 'free -m', 'ip a').
- If NO (it's a generic or simple request): Output 'SKIP'.

RULES:
1. ONLY output safe, read-only commands. NEVER output 'rm', 'sudo', 'dd', 'mkfs', or anything destructive.
2. Keep it to a single, simple command.
3. Output NOTHING else — no explanation, no markdown."""


def get_fix_prompt(bad_command: str, error_msg: str, distro_name: str) -> str:
    """Prompt for the self-healing loop when a command fails."""
    return (
        f"The command '{bad_command}' failed with this error:\n"
        f"{error_msg}\n\n"
        f"Fix the command to work on {distro_name}.\n"
        f"Output ONLY the fixed command. No markdown, no backticks, no explanations."
    )


def get_explain_prompt(command: str) -> str:
    """Prompt to explain a command in plain English."""
    return (
        f"Explain exactly what this Linux command does in simple, plain terms:\n"
        f"'{command}'\n\n"
        f"Be concise — 2-3 sentences max."
    )


EXPLAIN_SYSTEM = "You are a helpful and concise Linux tutor."

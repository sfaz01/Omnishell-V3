"""
Command safety validation — blocklist patterns and pre-execution checks.
"""

import re
import logging

logger = logging.getLogger(__name__)

# Patterns that should NEVER be executed, regardless of mode
BLOCKLIST_PATTERNS = [
    r"rm\s+(-[a-zA-Z]*)?r[a-zA-Z]*\s+/\s*$",   # rm -rf /
    r"rm\s+(-[a-zA-Z]*)?r[a-zA-Z]*\s+/\*",       # rm -rf /*
    r"mkfs\.",                                      # mkfs.ext4, etc.
    r"dd\s+if=.*of=/dev/",                         # dd overwriting disks
    r":\(\)\s*\{\s*:\|:\s*&\s*\}\s*;",             # fork bomb
    r">\s*/dev/sd[a-z]",                           # overwrite disk
    r"chmod\s+(-R\s+)?777\s+/\s*$",               # chmod 777 /
    r"wget.*\|\s*(ba)?sh",                         # piping wget to shell
    r"curl.*\|\s*(ba)?sh",                         # piping curl to shell
    r"mv\s+/\s",                                   # mv / somewhere
    r"echo\s+.*>\s*/etc/passwd",                   # overwriting passwd
    r"echo\s+.*>\s*/etc/shadow",                   # overwriting shadow
]

# Commands that require explicit user confirmation even in pro mode
SUDO_WARNING_PATTERNS = [
    r"^sudo\s+",
    r"systemctl\s+(stop|disable|mask)",
    r"apt\s+(remove|purge|autoremove)",
    r"pacman\s+-R",
    r"dnf\s+(remove|erase)",
    r"yum\s+(remove|erase)",
]


def is_blocked(command: str) -> bool:
    """
    Check if a command matches any blocklist pattern.
    Returns True if the command should be BLOCKED.
    """
    for pattern in BLOCKLIST_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            logger.warning(f"BLOCKED dangerous command: {command}")
            return True
    return False


def needs_sudo_warning(command: str) -> bool:
    """Check if a command involves sudo or destructive system operations."""
    for pattern in SUDO_WARNING_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            return True
    return False


def sanitize_command(command: str) -> str:
    """
    Clean up LLM output — strip markdown backticks, extra whitespace, etc.
    """
    # Remove markdown code fences
    command = command.strip()
    if command.startswith("```"):
        lines = command.split("\n")
        # Remove first and last lines (``` markers)
        lines = [l for l in lines if not l.strip().startswith("```")]
        command = "\n".join(lines).strip()
    
    # Remove inline backticks
    command = command.strip("`")
    
    # Remove leading $ or # (shell prompt artifacts)
    if command.startswith("$ ") or command.startswith("# "):
        command = command[2:]
    
    return command.strip()

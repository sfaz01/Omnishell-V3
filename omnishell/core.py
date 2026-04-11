"""
Core system utilities — OS detection, command execution, and logging setup.
"""

import os
import subprocess
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def setup_logging(log_file: str = "omnishell.log") -> None:
    """Configure logging for the application."""
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )


def detect_system_info() -> tuple[str, str]:
    """
    Auto-detect the Linux distribution and package manager.
    Returns (distro_name, package_manager).
    """
    try:
        import distro

        distro_id = distro.id()
        distro_name = distro.name(pretty=True)

        pkg_managers = {
            "arch": "pacman",
            "cachyos": "pacman",
            "manjaro": "pacman",
            "endeavouros": "pacman",
            "ubuntu": "apt",
            "debian": "apt",
            "linuxmint": "apt",
            "pop": "apt",
            "kali": "apt",
            "fedora": "dnf",
            "centos": "yum",
            "rhel": "yum",
            "rocky": "dnf",
            "alma": "dnf",
            "opensuse-leap": "zypper",
            "opensuse-tumbleweed": "zypper",
            "alpine": "apk",
            "void": "xbps-install",
            "gentoo": "emerge",
            "nixos": "nix-env",
        }

        pkg_mgr = pkg_managers.get(distro_id, "unknown")

        # CachyOS sometimes reports weird distro IDs
        if "cachyos" in distro_name.lower():
            pkg_mgr = "pacman"

        return distro_name, pkg_mgr

    except ImportError:
        logger.warning("distro package not installed, falling back to generic detection")
        return "Linux", "unknown"
    except Exception as e:
        logger.warning(f"Could not detect distro: {e}")
        return "Linux", "unknown"


def execute_command(command: str, silent: bool = False) -> tuple[bool, str]:
    """
    Execute a shell command and return (success, output).

    Args:
        command: The shell command to run.
        silent: If True, don't print output (used for diagnostic commands).

    Returns:
        Tuple of (success_bool, combined_output_string).
    """
    try:
        result = subprocess.run(
            command,
            shell=True,
            text=True,
            capture_output=True,
            timeout=120,  # 2 minute timeout to prevent hangs
        )

        output = result.stdout + result.stderr
        success = result.returncode == 0

        if not silent:
            if success and result.stdout:
                print(result.stdout)
            elif not success:
                print(f"\n❌ Error:\n{result.stderr}")

        return success, output

    except subprocess.TimeoutExpired:
        logger.error(f"Command timed out: {command}")
        return False, "Command timed out after 120 seconds."
    except Exception as e:
        logger.error(f"Command execution error: {e}")
        return False, str(e)


def get_config_dir() -> Path:
    """Get or create the OmniShell config directory (~/.config/omnishell)."""
    config_dir = Path.home() / ".config" / "omnishell"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir

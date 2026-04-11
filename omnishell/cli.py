"""
OmniShell CLI — Rich-powered interactive terminal interface.
"""

import os
import sys
import argparse
import logging

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.prompt import Prompt
from rich.spinner import Spinner
from rich.live import Live
from rich.syntax import Syntax
from rich.markdown import Markdown
from rich import box
from langchain_core.messages import SystemMessage, HumanMessage

from omnishell import __version__
from omnishell.core import detect_system_info, execute_command, setup_logging
from omnishell.llm import get_llm, invoke_llm, PROVIDERS, DEFAULT_MODELS
from omnishell.prompts import (
    get_system_prompt,
    get_diagnostic_prompt,
    get_fix_prompt,
    get_explain_prompt,
    EXPLAIN_SYSTEM,
)
from omnishell.safety import is_blocked, needs_sudo_warning, sanitize_command
from omnishell.history import save_command, get_history, clear_history, get_history_stats
from omnishell.memory import ConversationMemory

console = Console()
logger = logging.getLogger(__name__)


def print_banner(distro_name: str, pkg_manager: str, mode: str, provider: str):
    """Print the startup banner with system info."""
    banner_text = Text()
    banner_text.append("🧠 OmniShell", style="bold magenta")
    banner_text.append(f" v{__version__}", style="dim")
    
    info_table = Table(show_header=False, box=None, padding=(0, 2))
    info_table.add_column(style="bold cyan")
    info_table.add_column(style="white")
    info_table.add_row("System", distro_name)
    info_table.add_row("Package Manager", pkg_manager)
    info_table.add_row("Mode", f"[bold {'red' if mode == 'god' else 'green' if mode == 'pro' else 'yellow'}]{mode.upper()}[/]")
    info_table.add_row("LLM Provider", provider)

    console.print(Panel(
        info_table,
        title=banner_text,
        border_style="bright_blue",
        padding=(1, 2),
    ))
    console.print(
        "[dim]Commands: [bold]exit[/] quit • [bold]history[/] view past commands • "
        "[bold]clear[/] reset memory • [bold]stats[/] show statistics[/]\n"
    )


def print_history_table():
    """Display command history as a Rich table."""
    records = get_history(limit=15)
    if not records:
        console.print("[dim]No command history yet.[/]")
        return

    table = Table(
        title="📜 Command History",
        box=box.ROUNDED,
        border_style="blue",
        title_style="bold cyan",
    )
    table.add_column("#", style="dim", width=4)
    table.add_column("Time", style="cyan", width=20)
    table.add_column("Query", style="white", max_width=30)
    table.add_column("Command", style="green", max_width=40)
    table.add_column("Status", width=8)

    for r in records:
        status_icon = "✅" if r["status"] == "success" else "❌"
        timestamp = r["timestamp"][:19].replace("T", " ")
        table.add_row(
            str(r["id"]),
            timestamp,
            r["query"][:30],
            r["command"][:40],
            status_icon,
        )

    console.print(table)


def print_stats():
    """Display command history statistics."""
    stats = get_history_stats()
    table = Table(title="📊 Statistics", box=box.ROUNDED, border_style="magenta")
    table.add_column("Metric", style="bold")
    table.add_column("Value", justify="right")
    table.add_row("Total Commands", str(stats["total"]))
    table.add_row("Successful", f"[green]{stats['success']}[/]")
    table.add_row("Failed", f"[red]{stats['failed']}[/]")
    if stats["total"] > 0:
        rate = round(stats["success"] / stats["total"] * 100, 1)
        table.add_row("Success Rate", f"[bold]{rate}%[/]")
    console.print(table)


def run_diagnostics(llm, user_query: str) -> str:
    """Run a diagnostic command to gather system context."""
    diagnostic_prompt = get_diagnostic_prompt(user_query)
    msgs = [HumanMessage(content=diagnostic_prompt)]
    diag_cmd = invoke_llm(llm, msgs)
    diag_cmd = sanitize_command(diag_cmd)

    if "SKIP" in diag_cmd or "sudo" in diag_cmd.lower() or len(diag_cmd) > 200:
        return ""

    console.print(f"  [dim]👁️  Scanning: {diag_cmd}[/]")
    success, output = execute_command(diag_cmd, silent=True)
    if success:
        return output[:2000]
    return ""


def process_request(
    llm, user_input: str, mode: str, distro_name: str, pkg_manager: str,
    provider: str, memory: ConversationMemory, dry_run: bool = False
):
    """Process a single user request through the full pipeline."""
    memory.add_user_message(user_input)

    # Phase 1: Diagnostics
    with console.status("[bold blue]Analyzing request...", spinner="dots"):
        context_output = run_diagnostics(llm, user_input)

        # Phase 2: Build prompt with conversation memory
        context = memory.get_context_summary()
        system_prompt = get_system_prompt(distro_name, pkg_manager, mode, context_output)
        if context:
            system_prompt += f"\n\n{context}"

        msgs = [SystemMessage(content=system_prompt), HumanMessage(content=user_input)]
        candidate_cmd = invoke_llm(llm, msgs)
        candidate_cmd = sanitize_command(candidate_cmd)

    # Safety checks
    if "SAFE_MODE_ERROR" in candidate_cmd and mode != "god":
        console.print(Panel(
            "🛡️  This request was blocked for safety reasons.",
            border_style="red",
            title="Safe Mode",
        ))
        return

    if is_blocked(candidate_cmd):
        console.print(Panel(
            f"🛡️  Blocked dangerous command: [red]{candidate_cmd}[/]",
            border_style="red",
            title="Security Block",
        ))
        return

    memory.add_ai_message(candidate_cmd)

    # God mode: auto-execute
    if mode == "god" and not dry_run:
        console.print(f"  [bold red]🔥 GOD MODE:[/] {candidate_cmd}")
        logging.info(f"GOD MODE EXECUTING: {candidate_cmd}")
        success, output = execute_command(candidate_cmd)
        save_command(user_input, candidate_cmd, "success" if success else "failed", output, mode, provider)
        return

    # Review loop
    while True:
        console.print()
        console.print(Panel(
            Syntax(candidate_cmd, "bash", theme="monokai", line_numbers=False),
            title="🤖 Suggested Command",
            border_style="green",
            padding=(0, 2),
        ))

        if needs_sudo_warning(candidate_cmd):
            console.print("  [bold yellow]⚠️  This command requires elevated privileges[/]")

        if dry_run:
            console.print("  [dim italic]🏃 Dry-run mode — command will NOT be executed[/]")
            save_command(user_input, candidate_cmd, "dry-run", "", mode, provider)
            break

        choice = Prompt.ask(
            "  [bold]Action[/]",
            choices=["e", "x", "s"],
            default="e",
            show_choices=False,
        )

        if choice == "x":
            # Explain the command
            with console.status("[bold blue]Explaining...", spinner="dots"):
                explain_msgs = [
                    SystemMessage(content=EXPLAIN_SYSTEM),
                    HumanMessage(content=get_explain_prompt(candidate_cmd)),
                ]
                explanation = invoke_llm(llm, explain_msgs)

            console.print()
            console.print(Panel(
                Markdown(explanation),
                title="ℹ️  Explanation",
                border_style="cyan",
                padding=(1, 2),
            ))
            continue

        elif choice == "e":
            # Execute
            logging.info(f"EXECUTING: {candidate_cmd}")
            success, output = execute_command(candidate_cmd)

            if success:
                console.print("  [bold green]✅ Command executed successfully.[/]")
                save_command(user_input, candidate_cmd, "success", output, mode, provider)
                break
            else:
                save_command(user_input, candidate_cmd, "failed", output, mode, provider)
                console.print()
                console.print("  [bold yellow]🩹 Command failed. Auto-fixing...[/]")

                with console.status("[bold yellow]Healing...", spinner="dots"):
                    fix_msgs = [
                        SystemMessage(content=get_system_prompt(distro_name, pkg_manager, mode)),
                        HumanMessage(content=get_fix_prompt(candidate_cmd, output, distro_name)),
                    ]
                    candidate_cmd = invoke_llm(llm, fix_msgs)
                    candidate_cmd = sanitize_command(candidate_cmd)

                console.print("  [bold cyan]💡 New suggestion based on the error:[/]")
                continue

        elif choice == "s":
            console.print("  [dim]Skipped.[/]")
            break


def main():
    """Entry point for the OmniShell CLI."""
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="OmniShell — Self-Healing AI Terminal Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  omni                           Interactive mode\n"
            '  omni "update my system"        Single command mode\n'
            "  omni --mode newbie             Beginner-friendly mode\n"
            "  omni --provider ollama         Use local Ollama LLM\n"
            "  omni --dry-run                 Preview without executing\n"
        ),
    )
    parser.add_argument("query", nargs="?", help="Run a single command and exit")
    parser.add_argument(
        "--mode", choices=["newbie", "pro", "god"], default="pro",
        help="Safety level (default: pro)",
    )
    parser.add_argument(
        "--provider", choices=PROVIDERS, default=None,
        help=f"LLM provider (default: env OMNISHELL_PROVIDER or groq)",
    )
    parser.add_argument(
        "--model", default=None,
        help="Override the LLM model name",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show commands without executing them",
    )
    parser.add_argument(
        "--version", action="version", version=f"OmniShell v{__version__}",
    )

    args = parser.parse_args()

    # Setup
    setup_logging()
    provider = args.provider or os.getenv("OMNISHELL_PROVIDER", "groq")

    try:
        llm = get_llm(provider=provider, model=args.model)
    except ValueError as e:
        console.print(f"[bold red]❌ {e}[/]")
        sys.exit(1)

    distro_name, pkg_manager = detect_system_info()
    memory = ConversationMemory()

    # Single command mode
    if args.query:
        process_request(llm, args.query, args.mode, distro_name, pkg_manager, provider, memory, args.dry_run)
        return

    # Interactive mode
    print_banner(distro_name, pkg_manager, args.mode, provider)

    while True:
        try:
            user_input = Prompt.ask("[bold cyan]USER[/]")
            cmd = user_input.strip().lower()

            if cmd in ("exit", "quit", "q"):
                console.print("[dim]👋 Goodbye![/]")
                break
            if not user_input.strip():
                continue
            if cmd == "history":
                print_history_table()
                continue
            if cmd == "stats":
                print_stats()
                continue
            if cmd == "clear":
                memory.clear()
                console.print("[dim]🧹 Conversation memory cleared.[/]")
                continue
            if cmd == "clear history":
                clear_history()
                console.print("[dim]🧹 Command history cleared.[/]")
                continue

            process_request(
                llm, user_input, args.mode, distro_name, pkg_manager,
                provider, memory, args.dry_run,
            )

        except KeyboardInterrupt:
            console.print("\n[dim]👋 Goodbye![/]")
            break
        except Exception as e:
            console.print(f"[bold red]❌ Error: {e}[/]")
            logger.error(f"Unhandled error: {e}", exc_info=True)


if __name__ == "__main__":
    main()

from typing import Any, Dict, List, Optional
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TimeElapsedColumn,
)
from rich.table import Table
from rich.align import Align
from rich.traceback import install
from rich.theme import Theme
import time

# Custom theme for FiNo
custom_theme = Theme(
    {
        "info": "cyan",
        "warning": "yellow",
        "danger": "red",
        "success": "green",
        "magic": "bright_magenta",
    }
)

# Shared Rich console with custom theme
console = Console(
    theme=custom_theme, markup=True, emoji=True, force_terminal=True, color_system="256"
)

# Pretty tracebacks
install(show_locals=False, console=console)


def print_header(title: str, subtitle: Optional[str] = None) -> None:
    """Print a SICK header with title and optional subtitle"""
    header_text = Text(f"🔥 {title}", style="bright_magenta bold")
    if subtitle:
        header_text.append(f"\n{subtitle}", style="cyan")

    panel = Panel(
        Align.center(header_text),
        border_style="bright_magenta",
        padding=(1, 2),
        title="[bold]FiNo[/bold]",
        subtitle="[italic]Secure File Sharing[/italic]",
    )
    console.print(panel)


def print_step(step_num: int, title: str, status: str = "working") -> None:
    """Print a step with status indicator"""
    step_emoji = "🔄" if status == "working" else "✅" if status == "success" else "❌"
    step_style = (
        "cyan" if status == "working" else "green" if status == "success" else "red"
    )

    console.print(
        f"{step_emoji} [bold]Step {step_num}:[/bold] {title}", style=step_style
    )


def print_feature_badge(feature: str, enabled: bool = True) -> None:
    """Print a feature badge"""
    if enabled:
        console.print(f"🎭 [bold]{feature}[/bold]", style="bright_magenta")
    else:
        console.print(f"⚪ {feature}", style="dim")


def create_progress_bar(description: str):
    """Create a progress bar for operations"""
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console,
    )


def print_file_info(
    filename: str, size: int, features: Optional[List[Any]] = None
) -> None:
    """Print file information in a beautiful table"""
    table = Table(title="📁 File Information", show_header=True, header_style="bold magenta")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="white")

    table.add_row("Filename", filename)
    table.add_row("Size", f"{size:,} bytes")

    if features:
        for feature in features:
            table.add_row("Feature", f"🎭 {feature}")

    console.print(table)


def animate_loading(description: str, duration: float = 2.0) -> None:
    """Animate a loading spinner"""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task(description, total=None)
        time.sleep(duration)
        progress.update(task, completed=True)


def print_success_message(
    message: str, details: Optional[Dict[str, Any]] = None
) -> None:
    """Print a success message with optional details"""
    success_panel = Panel(Text(f"🎉 {message}", style="bright_green bold"), border_style="green")
    console.print(success_panel)

    if details:
        table = Table(show_header=False, box=None)
        table.add_column("Key", style="cyan")
        table.add_column("Value", style="white")

        for key, value in details.items():
            table.add_row(key, str(value))

        console.print(table)


def print_error_message(message: str, error: Optional[Exception] = None) -> None:
    """Print an error message with optional exception details"""
    error_panel = Panel(Text(f"❌ {message}", style="bright_red bold"), border_style="red")
    console.print(error_panel)

    if error:
        console.print(f"Error details: {error}", style="red")


def print_warning_message(message: str) -> None:
    """Print a warning message"""
    warning_panel = Panel(Text(f"⚠️ {message}", style="bright_yellow bold"), border_style="yellow")
    console.print(warning_panel)

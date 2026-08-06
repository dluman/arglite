from rich.console import Console
from rich.table import Table

from .flag import Flag


def render(flags: dict[str, Flag]) -> None:
    """Display a help table of all declared flags."""
    table = Table(title="CLI flags")
    table.add_column("Variable name")
    table.add_column("Short flag")
    table.add_column("Variable type")
    table.add_column("Default")
    table.add_column("Required")
    table.add_column("Description")

    for name, flag in flags.items():
        short = f"-{flag.short}" if flag.short else ""
        table.add_row(
            f"--{name}",
            short,
            flag.type.__name__ if flag.type else "inferred",
            str(flag.default),
            "yes" if flag.required else "no",
            flag.help or "",
        )

    console = Console()
    console.print(table)


def show_summary() -> None:
    """Print the short summary text shown before the help table."""
    console = Console()
    console.print("arglite\n\nA lightweight, explicit CLI argument parser.\n")

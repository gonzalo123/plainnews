from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

_console: Console | None = None


def get_console() -> Console:
    global _console

    if _console is None:
        _console = Console()

    return _console


def print_result(title: str, content: str) -> None:
    console = get_console()
    console.print(Panel(Markdown(content), title=title, border_style="green"))

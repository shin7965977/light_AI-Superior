from rich.align import Align
from rich.console import Console, Group
from rich.panel import Panel
from rich.text import Text


def render_light_bulb(is_on: bool, brightness: float) -> Panel:
    """Renders a dynamic ANSI ASCII light bulb using rich."""
    pct = int(brightness * 100) if is_on else 0

    if not is_on or brightness <= 0.0:
        # OFF / Dark Gray State
        bulb_art = """
            .---.
           /     \\
          |  ( )  |
           \\     /
            `---'
            |===|
            '---'
        """
        color = "dim grey50"
        status_text = "[dim red]● OFF[/dim red]  |  Brightness: [dim white]0%[/dim white]"
        bar = "[dim grey30]░░░░░░░░░░░░░░░░░░░░[/dim grey30]"
    else:
        # ON State with dynamic brightness colors and rays
        filled_slots = int(brightness * 20)
        empty_slots = 20 - filled_slots

        if brightness < 0.3:
            color = "yellow3"
            aura = "       "
            bar_color = "yellow3"
        elif brightness < 0.7:
            color = "bright_yellow"
            aura = " \\ | / "
            bar_color = "bright_yellow"
        else:
            color = "bold bright_yellow"
            aura = "*-/|\\-*"
            bar_color = "bold gold1"

        bulb_art = f"""
           {aura}
            .---.
          -/( @ )\\-
          | (@@@) |
          -\\     /-
            `---'
            |===|
            '---'
        """
        status_text = f"[bold green]● ON[/bold green]   |  Brightness: [bold {color}]{pct}%[/bold {color}]"
        bar = f"[{bar_color}]{'█' * filled_slots}[/{bar_color}][dim grey30]{'░' * empty_slots}[/dim grey30]"

    art_text = Text(bulb_art.strip("\n"), style=color, justify="center")
    info_text = Text.from_markup(f"{status_text}\n{bar}", justify="center")

    panel_content = Group(
        Align.center(art_text),
        Align.center(info_text)
    )

    return Panel(
        panel_content,
        title="[bold cyan]💡 Virtual Smart Light Bulb[/bold cyan]",
        subtitle="[dim]Powered by Gemini 3.5 Flash[/dim]",
        border_style="cyan" if is_on else "dim grey50",
        expand=False,
        padding=(1, 4),
    )


if __name__ == "__main__":
    console = Console()
    console.print(render_light_bulb(False, 0.0))
    console.print(render_light_bulb(True, 0.7))

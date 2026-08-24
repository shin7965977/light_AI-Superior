from rich.align import Align
from rich.console import Console, Group
from rich.panel import Panel
from rich.text import Text


def render_light_bulb(is_on: bool, brightness: float) -> Panel:
    """Renders a dynamic ANSI ASCII light bulb with rich TrueColor gradients and filament stages."""
    pct = int(brightness * 100) if is_on else 0

    if not is_on or brightness <= 0.0:
        # 0% / OFF State: Dark Gray
        color = "#555555"
        border_color = "#444444"
        bulb_art = """
            .---.
           /     \\
          | (   ) |
           \\     /
            `---'
            |===|
            '---'
        """
        status_text = "[dim red]● OFF[/dim red]  |  Brightness: [dim white]0%[/dim white]"
        bar = "[#333333]░░░░░░░░░░░░░░░░░░░░[/#333333]"

    elif brightness <= 0.30:
        # 1% ~ 30%: Dim Amber / Dark Orange Glow
        color = "#D2691E"  # Warm Chocolate Amber
        border_color = "#D2691E"
        filled_slots = max(1, int(brightness * 20))
        empty_slots = 20 - filled_slots

        bulb_art = """
            .---.
          -/(   )\\-
          | ( . ) |
          -\\ . / -
            `---'
            |===|
            '---'
        """
        status_text = f"[bold green]● ON[/bold green]   |  Brightness: [bold {color}]{pct}% (Dim)[/bold {color}]"
        bar = f"[{color}]{'█' * filled_slots}[/{color}][#333333]{'░' * empty_slots}[/#333333]"

    elif brightness <= 0.70:
        # 31% ~ 70%: Vibrant Warm Golden Yellow
        color = "#FFD700"  # Gold Yellow
        border_color = "#FFD700"
        filled_slots = max(1, int(brightness * 20))
        empty_slots = 20 - filled_slots

        bulb_art = """
           \\ | /
            .---.
          -/( o )\\-
          | ( * ) |
          -\\ * / -
            `---'
            |===|
            '---'
        """
        status_text = f"[bold green]● ON[/bold green]   |  Brightness: [bold {color}]{pct}% (Medium)[/bold {color}]"
        bar = f"[{color}]{'█' * filled_slots}[/{color}][#333333]{'░' * empty_slots}[/#333333]"

    else:
        # 71% ~ 100%: Blazing Radiant Neon Gold-White
        color = "#FFFF55"  # Neon White-Gold
        border_color = "#FFFF77"
        filled_slots = max(1, int(brightness * 20))
        empty_slots = 20 - filled_slots

        bulb_art = """
          *-/|\\-*
            .---.
          -/(@@@)\\-
          | (@#@) |
          -\\(#)/ -
            `---'
            |===|
            '---'
        """
        status_text = f"[bold green]● ON[/bold green]   |  Brightness: [bold {color}]{pct}% (Bright!)[/bold {color}]"
        bar = f"[{color}]{'█' * filled_slots}[/{color}][#333333]{'░' * empty_slots}[/#333333]"

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
        border_style=border_color,
        expand=False,
        padding=(1, 4),
    )


if __name__ == "__main__":
    console = Console()
    console.print(render_light_bulb(False, 0.0))
    console.print(render_light_bulb(True, 0.25))
    console.print(render_light_bulb(True, 0.50))
    console.print(render_light_bulb(True, 1.0))

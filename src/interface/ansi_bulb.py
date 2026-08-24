from rich.align import Align
from rich.console import Group
from rich.panel import Panel
from rich.text import Text


def render_light_bulb(is_on: bool, brightness: float) -> Panel:
    """Renders a dynamic ANSI ASCII light bulb with high-contrast, universally distinct color tiers."""
    pct = int(brightness * 100) if is_on else 0

    if not is_on or brightness <= 0.0:
        # 0% / OFF State: Dim Gray / Dark
        color = "dim grey62"
        border_color = "dim grey42"
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
        bar = "[dim grey30]░░░░░░░░░░░░░░░░░░░░[/dim grey30]"

    elif brightness <= 0.30:
        # 1% ~ 30%: High-Contrast Deep Orange / Amber (Cannot be confused with yellow)
        color = "bold dark_orange3"
        border_color = "dark_orange"
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
        status_text = f"[bold green]● ON[/bold green]   |  Brightness: [{color}]{pct}% (Dim Amber)[/{color}]"
        bar = f"[{color}]{'█' * filled_slots}[/{color}][dim grey30]{'░' * empty_slots}[/dim grey30]"

    elif brightness <= 0.70:
        # 31% ~ 70%: Bright Golden Yellow
        color = "bold yellow"
        border_color = "yellow"
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
        status_text = f"[bold green]● ON[/bold green]   |  Brightness: [{color}]{pct}% (Warm Yellow)[/{color}]"
        bar = f"[{color}]{'█' * filled_slots}[/{color}][dim grey30]{'░' * empty_slots}[/dim grey30]"

    else:
        # 71% ~ 100%: Blazing Brilliant White-Hot (High visual impact against dark background)
        color = "bold bright_white"
        border_color = "bold bright_cyan"
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
        status_text = f"[bold green]● ON[/bold green]   |  Brightness: [{color}]{pct}% (White Hot!)[/{color}]"
        bar = f"[{color}]{'█' * filled_slots}[/{color}][dim grey30]{'░' * empty_slots}[/dim grey30]"

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

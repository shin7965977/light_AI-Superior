import os
from pathlib import Path

from dotenv import load_dotenv
from rich.console import Console
from rich.prompt import Prompt

# Load existing .env if available
load_dotenv()

ENV_FILE_PATH = Path(".env")


def get_api_key() -> str | None:
    """Retrieves the Gemini API key from environment variables (ephemeral in-memory)."""
    return os.getenv("GEMINI_API_KEY")


def get_model_name() -> str:
    """Retrieves the configured Gemini model name, defaulting to gemini-3.5-flash."""
    return os.getenv("GEMINI_MODEL", "gemini-3.5-flash")


def ensure_api_key_interactive(console: Console | None = None) -> str | None:
    """Interactive onboarding routine to ensure an API key is present for the current session only.

    The key is kept strictly in-memory (ephemeral) and is never persisted to disk,
    guaranteeing that every new session will always prompt the user.
    """
    console = console or Console()

    console.print("\n[bold yellow]🔑 Gemini API Authentication[/bold yellow]")
    console.print("[dim]Please paste your Gemini API key below for this session.[/dim]")
    console.print("[dim](Press Enter without input to continue in offline/regex-only mode)[/dim]\n")

    user_key = Prompt.ask("[bold cyan]Enter Gemini API Key[/bold cyan]", console=console, password=True)

    if user_key and user_key.strip():
        clean_key = user_key.strip()
        os.environ["GEMINI_API_KEY"] = clean_key
        console.print("[bold green]✔ API Key loaded for this session (ephemeral/not saved to disk).[/bold green]\n")
        return clean_key

    # Explicitly clear environment variable for offline mode
    if "GEMINI_API_KEY" in os.environ:
        del os.environ["GEMINI_API_KEY"]

    console.print("[yellow]⚠ Running in offline/fallback mode (Regex only).[/yellow]\n")
    return None

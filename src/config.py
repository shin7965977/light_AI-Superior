import os
from pathlib import Path

from dotenv import load_dotenv
from rich.console import Console
from rich.prompt import Prompt

# Load existing .env if available
load_dotenv()

ENV_FILE_PATH = Path(".env")


def get_api_key() -> str | None:
    """Retrieves the Gemini API key from environment variables or .env file."""
    load_dotenv(override=True)
    return os.getenv("GEMINI_API_KEY")


def get_model_name() -> str:
    """Retrieves the configured Gemini model name, defaulting to gemini-3.5-flash."""
    load_dotenv(override=True)
    return os.getenv("GEMINI_MODEL", "gemini-3.5-flash")


def save_api_key_to_env(api_key: str) -> None:
    """Persists the provided API key into the local .env file."""
    api_key = api_key.strip()
    env_content = ""
    key_found = False

    if ENV_FILE_PATH.exists():
        lines = ENV_FILE_PATH.read_text(encoding="utf-8").splitlines()
        new_lines = []
        for line in lines:
            if line.startswith("GEMINI_API_KEY="):
                new_lines.append(f"GEMINI_API_KEY={api_key}")
                key_found = True
            else:
                new_lines.append(line)
        if not key_found:
            new_lines.append(f"GEMINI_API_KEY={api_key}")
        env_content = "\n".join(new_lines) + "\n"
    else:
        env_content = f"GEMINI_API_KEY={api_key}\nGEMINI_MODEL=gemini-3.5-flash\n"

    ENV_FILE_PATH.write_text(env_content, encoding="utf-8")
    os.environ["GEMINI_API_KEY"] = api_key
    load_dotenv(override=True)


def ensure_api_key_interactive(console: Console | None = None) -> str | None:
    """Interactive onboarding routine to ensure an API key is present."""
    console = console or Console()
    api_key = get_api_key()

    if api_key and api_key.strip():
        return api_key.strip()

    console.print("\n[bold yellow]🔑 Gemini API Key Not Found![/bold yellow]")
    console.print("[dim]To use AI natural language control, please paste your Gemini API key below.[/dim]")
    console.print("[dim](Press Enter without input to continue in offline/regex-only mode)[/dim]\n")

    user_key = Prompt.ask("[bold cyan]Enter Gemini API Key[/bold cyan]", console=console, password=True)

    if user_key and user_key.strip():
        save_api_key_to_env(user_key)
        console.print("[bold green]✔ API Key successfully saved to .env file![/bold green]\n")
        return user_key.strip()

    console.print("[yellow]⚠ Running in offline/fallback mode (Regex only).[/yellow]\n")
    return None

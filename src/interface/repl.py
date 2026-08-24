import asyncio

from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout
from rich.console import Console

from light_bulb import LightBulb
from src.adapters.gemini_parser import GeminiParser
from src.config import ensure_api_key_interactive
from src.interface.ansi_bulb import render_light_bulb
from src.observability import get_logger
from src.ports.action_schema import ActionSchema, ActionType, BulbContext
from src.ports.base_parser import BaseParser

logger = get_logger()


class LightBulbCLI:
    """Asynchronous interactive CLI REPL for controlling the LightBulb."""

    def __init__(
        self,
        bulb: LightBulb | None = None,
        parser: BaseParser | None = None,
        console: Console | None = None,
        session: PromptSession | None = None,
    ):
        self.bulb = bulb or LightBulb()
        self.parser = parser or GeminiParser()
        self.console = console or Console()
        self._session = session

    @property
    def session(self) -> PromptSession:
        if self._session is None:
            self._session = PromptSession()
        return self._session

    def get_context(self) -> BulbContext:
        return BulbContext(
            is_on=self.bulb.is_on,
            brightness=self.bulb.brightness,
        )

    def display_ui(self) -> None:
        """Renders the current state of the light bulb."""
        self.console.clear()
        self.console.print(render_light_bulb(self.bulb.is_on, self.bulb.brightness))
        self.console.print("[dim]Type your command (e.g. 'turn on', 'dim by 20%', 'set to 70%') or 'exit' to quit:[/dim]\n")

    async def execute_action(self, action: ActionSchema) -> None:
        """Executes the resolved action on the domain LightBulb."""
        if action.action == ActionType.TURN_ON:
            self.bulb.turn_on()
        elif action.action == ActionType.TURN_OFF:
            self.bulb.turn_off()
        elif action.action == ActionType.SET_BRIGHTNESS:
            if action.value is not None:
                # If setting brightness > 0 while bulb is OFF, also turn it on
                if not self.bulb.is_on and action.value > 0.0:
                    self.bulb.is_on = True
                self.bulb.set_brightness(action.value)
        elif action.action == ActionType.UNKNOWN:
            self.console.print("[yellow]❓ Could not understand command. Please try again (e.g. 'turn on', 'dim by 20%').[/yellow]")

    async def run(self) -> None:
        """Runs the interactive async REPL."""
        ensure_api_key_interactive(self.console)
        self.display_ui()

        while True:
            try:
                with patch_stdout():
                    user_input = await self.session.prompt_async(">>> User: ")
            except (EOFError, KeyboardInterrupt):
                self.console.print("\n[bold cyan]Goodbye! 👋[/bold cyan]")
                break

            text = user_input.strip()
            if not text:
                continue

            if text.lower() in ["exit", "quit", "q"]:
                self.console.print("[bold cyan]Goodbye! 👋[/bold cyan]")
                break

            context = self.get_context()
            action = await self.parser.parse(text, context)

            await self.execute_action(action)
            await asyncio.sleep(0.5)
            self.display_ui()

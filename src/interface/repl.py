import asyncio

from prompt_toolkit import PromptSession
from prompt_toolkit.patch_stdout import patch_stdout
from rich.console import Console

from light_bulb import LightBulb
from src.adapters.gemini_parser import GeminiParser
from src.config import ensure_api_key_interactive, get_api_key
from src.interface.ansi_bulb import render_light_bulb
from src.observability import get_logger
from src.ports.action_schema import ActionSchema, ActionType, BulbContext
from src.ports.base_parser import BaseParser

logger = get_logger()


class LightBulbCLI:
    """Asynchronous interactive CLI REPL for controlling the LightBulb with Disambiguation support."""

    def __init__(
        self,
        bulb: LightBulb | None = None,
        parser: BaseParser | None = None,
        console: Console | None = None,
        session: PromptSession | None = None,
    ):
        self.bulb = bulb or LightBulb()
        self.parser = parser or GeminiParser()
        self.console = console or Console(force_terminal=True)
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
        """Renders the current state of the light bulb with dynamic parser engine badge."""
        self.console.clear()
        api_key = get_api_key()
        engine_name = "Gemini 3.5 Flash" if (api_key and api_key.strip()) else "Regex Engine"
        self.console.print(render_light_bulb(self.bulb.is_on, self.bulb.brightness, engine_name=engine_name))
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
        elif action.action == ActionType.CLARIFY:
            await self.handle_clarification(action)
        elif action.action == ActionType.UNKNOWN:
            self.console.print("[yellow]❓ Could not understand command. Please try again (e.g. 'turn on', 'dim by 20%').[/yellow]")

    async def handle_clarification(self, action: ActionSchema) -> None:
        """Handles interactive clarification dialogue when user intent is ambiguous."""
        prompt_text = action.clarification_prompt or "Your command was unclear. What would you like to do?"
        self.console.print(f"\n[bold cyan]❓ {prompt_text}[/bold cyan]")

        options = action.clarification_options or []
        if options:
            for idx, opt in enumerate(options, 1):
                self.console.print(f"  [bold yellow][{idx}][/bold yellow] {opt}")

            try:
                with patch_stdout():
                    choice = await self.session.prompt_async(f"\n>>> Choose option [1-{len(options)}]: ")
            except (EOFError, KeyboardInterrupt):
                return

            choice_str = choice.strip()
            if choice_str.isdigit() and 1 <= int(choice_str) <= len(options):
                chosen_command = options[int(choice_str) - 1]
                self.console.print(f"[dim]Executing: {chosen_command}[/dim]")
                resolved_action = await self.parser.parse(chosen_command, self.get_context())
                # Avoid recursive clarify if option resolved to an action
                if resolved_action.action != ActionType.CLARIFY:
                    await self.execute_action(resolved_action)
            elif choice_str:
                resolved_action = await self.parser.parse(choice_str, self.get_context())
                await self.execute_action(resolved_action)
        else:
            try:
                with patch_stdout():
                    followup = await self.session.prompt_async(">>> Please clarify: ")
            except (EOFError, KeyboardInterrupt):
                return
            if followup.strip():
                resolved_action = await self.parser.parse(followup.strip(), self.get_context())
                await self.execute_action(resolved_action)

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
            await asyncio.sleep(0.6)
            self.display_ui()

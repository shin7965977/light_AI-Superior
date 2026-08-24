import time

from src.adapters.regex_parser import RegexParser
from src.config import get_api_key, get_model_name
from src.observability import get_logger
from src.ports.action_schema import ActionSchema, BulbContext
from src.ports.base_parser import BaseParser

logger = get_logger()


SYSTEM_INSTRUCTION = """
You are an intelligent controller for a smart light bulb.
Your job is to parse user natural language input into a structured ActionSchema.

Current State Context:
- is_on: {is_on}
- brightness: {brightness} (range 0.0 to 1.0)

Rules:
1. "TURN_ON": Turns the light bulb on.
2. "TURN_OFF": Turns the light bulb off.
3. "SET_BRIGHTNESS": Sets the brightness to a specific float between 0.0 and 1.0.
   - For absolute requests (e.g. "set to 70%"), value is 0.7.
   - For relative changes (e.g. "dim by 20%"), calculate based on current brightness (e.g. 0.8 - 0.2 = 0.6).
   - Value must always be clamped to [0.0, 1.0].
4. "Toggle":
   - If current is_on is True, return TURN_OFF.
   - If current is_on is False, return TURN_ON.
5. Compound or Negation:
   - "Switch it back on instead of off" -> TURN_ON.
   - "Set it to 10% instead of 70%" -> SET_BRIGHTNESS with value 0.1.
6. Unrelated or Invalid Inputs:
   - If the input is not a light bulb command (e.g. "what is the weather today?"), return UNKNOWN with value null.
"""


class GeminiParser(BaseParser):
    """Primary parser utilizing Gemini 3.5 Flash with structured output and state context injection."""

    def __init__(self, fallback_parser: BaseParser | None = None):
        self.fallback_parser = fallback_parser or RegexParser()

    async def parse(self, text: str, context: BulbContext) -> ActionSchema:
        api_key = get_api_key()
        model_name = get_model_name()

        if not api_key:
            logger.warning("gemini_api_key_missing", fallback="regex")
            return await self.fallback_parser.parse(text, context)

        start_time = time.perf_counter()

        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=api_key)

            formatted_system = SYSTEM_INSTRUCTION.format(
                is_on=context.is_on,
                brightness=context.brightness,
            )

            response = client.models.generate_content(
                model=model_name,
                contents=text,
                config=types.GenerateContentConfig(
                    system_instruction=formatted_system,
                    response_mime_type="application/json",
                    response_schema=ActionSchema,
                    temperature=0.1,
                ),
            )

            latency_ms = (time.perf_counter() - start_time) * 1000

            # Parse structured output from response
            action: ActionSchema
            if response.parsed and isinstance(response.parsed, ActionSchema):
                action = response.parsed
            else:
                # Fallback to json text parsing if parsed attribute isn't directly loaded
                action = ActionSchema.model_validate_json(response.text or "{}")

            logger.info(
                "gemini_parse_success",
                input_text=text,
                action=action.action.value,
                value=action.value,
                latency_ms=round(latency_ms, 2),
                model=model_name,
            )
            return action

        except Exception as exc:  # noqa: BLE001
            latency_ms = (time.perf_counter() - start_time) * 1000
            logger.error(
                "gemini_parse_error",
                error=str(exc),
                latency_ms=round(latency_ms, 2),
                fallback="regex",
            )
            # Gracefully fallback to RegexParser upon API or network error
            return await self.fallback_parser.parse(text, context)

import re

from src.ports.action_schema import ActionSchema, ActionType, BulbContext
from src.ports.base_parser import BaseParser


class RegexParser(BaseParser):
    """Rule-based regex parser serving as fast-path, resilience fallback, and interactive clarification."""

    async def parse(self, text: str, context: BulbContext) -> ActionSchema:
        clean_text = text.strip().lower()

        # 1. Handle compound / negation patterns first
        if re.search(r"(?:switch|turn).*?back\s+on.*?instead.*?off", clean_text) or re.search(r"(?:switch|turn).*?on.*?instead.*?off", clean_text):
            return ActionSchema(action=ActionType.TURN_ON, reasoning="Regex matched compound on-instead-of-off pattern")

        if re.search(r"(?:switch|turn).*?back\s+off.*?instead.*?on", clean_text) or re.search(r"(?:switch|turn).*?off.*?instead.*?on", clean_text):
            return ActionSchema(action=ActionType.TURN_OFF, reasoning="Regex matched compound off-instead-of-on pattern")

        # 2. Handle Toggle
        if re.search(r"\b(toggle|flip|switch\s+state)\b", clean_text):
            next_action = ActionType.TURN_OFF if context.is_on else ActionType.TURN_ON
            return ActionSchema(action=next_action, reasoning="Regex resolved toggle based on current state")

        # 3. Handle Relative Brightness: reduce / dim / decrease / lower
        relative_decrease = re.search(r"(?:dim|reduce|decrease|lower|turn\s+down).*?(\d+)\s*%", clean_text)
        if relative_decrease:
            delta = float(relative_decrease.group(1)) / 100.0
            new_val = max(0.0, round(context.brightness - delta, 2))
            return ActionSchema(action=ActionType.SET_BRIGHTNESS, value=new_val, reasoning=f"Regex decreased brightness by {delta * 100}%")

        # 4. Handle Relative Brightness: increase / brighten / boost / turn up
        relative_increase = re.search(r"(?:brighten|increase|boost|turn\s+up|raise).*?(\d+)\s*%", clean_text)
        if relative_increase:
            delta = float(relative_increase.group(1)) / 100.0
            new_val = min(1.0, round(context.brightness + delta, 2))
            return ActionSchema(action=ActionType.SET_BRIGHTNESS, value=new_val, reasoning=f"Regex increased brightness by {delta * 100}%")

        # 5. Handle Absolute Brightness (e.g., "set brightness to 70%", "brightness 10%")
        absolute_match = re.search(r"(?:brightness\s+(?:to\s+)?|set\s+(?:it\s+)?to\s+)(\d{1,3})\s*%", clean_text)
        if absolute_match:
            val = float(absolute_match.group(1)) / 100.0
            val = max(0.0, min(1.0, val))
            return ActionSchema(action=ActionType.SET_BRIGHTNESS, value=val, reasoning="Regex matched absolute brightness")

        # 6. Handle Turn On (supports "turn on", "turn it on", "switch on", "turn the light on")
        if re.search(r"\b(?:turn|switch|power)\s+(?:the\s+light\s+|it\s+)?on\b", clean_text) or re.search(r"\blights?\s+on\b", clean_text):
            return ActionSchema(action=ActionType.TURN_ON, reasoning="Regex matched turn on pattern")

        # 7. Handle Turn Off (supports "turn off", "turn it off", "switch off", "turn the light off")
        if re.search(r"\b(?:turn|switch|power)\s+(?:the\s+light\s+|it\s+)?off\b", clean_text) or re.search(r"\blights?\s+off\b", clean_text):
            return ActionSchema(action=ActionType.TURN_OFF, reasoning="Regex matched turn off pattern")

        # 8. Interactive Clarification / Disambiguation Rules for Incomplete or Ambiguous Inputs
        # 8a. Isolated percentage without verb (e.g. "20%" or "70%")
        isolated_pct = re.fullmatch(r"(\d{1,3})\s*%", clean_text)
        if isolated_pct:
            pct_val = isolated_pct.group(1)
            return ActionSchema(
                action=ActionType.CLARIFY,
                reasoning="Ambiguous percentage value without explicit action verb",
                clarification_prompt=f"You entered '{pct_val}%'. What would you like to do?",
                clarification_options=[
                    f"Set brightness to {pct_val}%",
                    f"Dim brightness by {pct_val}%",
                    f"Increase brightness by {pct_val}%",
                ],
            )

        # 8b. Ambiguous "light" / "bulb"
        if clean_text in ["light", "the light", "bulb", "light bulb", "lights"]:
            return ActionSchema(
                action=ActionType.CLARIFY,
                reasoning="Ambiguous command: light noun without action verb",
                clarification_prompt="Your command is incomplete. What would you like to do with the light?",
                clarification_options=[
                    "Please turn the light on",
                    "Now please turn it off",
                    "Toggle the light",
                ],
            )

        # 8c. Ambiguous "turn" / "switch" / "power" without on/off
        if clean_text in ["turn", "switch", "power"]:
            return ActionSchema(
                action=ActionType.CLARIFY,
                reasoning="Ambiguous verb without state direction",
                clarification_prompt="Did you mean to switch the light ON or OFF?",
                clarification_options=[
                    "Turn on the light",
                    "Turn off the light",
                ],
            )

        # 8d. Ambiguous "brightness" without value
        if clean_text in ["brightness", "dim", "bright"]:
            return ActionSchema(
                action=ActionType.CLARIFY,
                reasoning="Ambiguous brightness keyword without target value",
                clarification_prompt="How would you like to adjust the brightness?",
                clarification_options=[
                    "Set brightness to 100%",
                    "Set brightness to 50%",
                    "Reduce the brightness by 20%",
                ],
            )

        # 8e. Common typo detection (e.g. "trun on", "tunr off", "dark")
        if re.search(r"\b(trun|tunr|swich)\s+on\b", clean_text) or "dark" in clean_text:
            return ActionSchema(
                action=ActionType.CLARIFY,
                reasoning="Typo or contextual hint detected",
                clarification_prompt="Did you mean to turn on the light?",
                clarification_options=[
                    "Please turn the light on",
                    "Set brightness to 100%",
                ],
            )

        if re.search(r"\b(trun|tunr|swich)\s+off\b", clean_text):
            return ActionSchema(
                action=ActionType.CLARIFY,
                reasoning="Typo detected",
                clarification_prompt="Did you mean to turn off the light?",
                clarification_options=[
                    "Now please turn it off",
                ],
            )

        return ActionSchema(action=ActionType.UNKNOWN, reasoning="Regex could not determine intent")

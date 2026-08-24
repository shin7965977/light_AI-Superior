import re

from src.ports.action_schema import ActionSchema, ActionType, BulbContext
from src.ports.base_parser import BaseParser


class RegexParser(BaseParser):
    """Rule-based regex parser serving as fast-path and resilience fallback."""

    async def parse(self, text: str, context: BulbContext) -> ActionSchema:
        clean_text = text.strip().lower()

        # Handle compound / negation patterns first
        if re.search(r"(?:switch|turn).*?back\s+on.*?instead.*?off", clean_text) or re.search(r"(?:switch|turn).*?on.*?instead.*?off", clean_text):
            return ActionSchema(action=ActionType.TURN_ON, reasoning="Regex matched compound on-instead-of-off pattern")

        if re.search(r"(?:switch|turn).*?back\s+off.*?instead.*?on", clean_text) or re.search(r"(?:switch|turn).*?off.*?instead.*?on", clean_text):
            return ActionSchema(action=ActionType.TURN_OFF, reasoning="Regex matched compound off-instead-of-on pattern")

        # Handle Toggle
        if re.search(r"\b(toggle|flip|switch\s+state)\b", clean_text):
            next_action = ActionType.TURN_OFF if context.is_on else ActionType.TURN_ON
            return ActionSchema(action=next_action, reasoning="Regex resolved toggle based on current state")

        # Handle Relative Brightness: reduce / dim / decrease / lower
        relative_decrease = re.search(r"(?:dim|reduce|decrease|lower|turn\s+down).*?(\d+)\s*%", clean_text)
        if relative_decrease:
            delta = float(relative_decrease.group(1)) / 100.0
            new_val = max(0.0, round(context.brightness - delta, 2))
            return ActionSchema(action=ActionType.SET_BRIGHTNESS, value=new_val, reasoning=f"Regex decreased brightness by {delta * 100}%")

        # Handle Relative Brightness: increase / brighten / boost / turn up
        relative_increase = re.search(r"(?:brighten|increase|boost|turn\s+up|raise).*?(\d+)\s*%", clean_text)
        if relative_increase:
            delta = float(relative_increase.group(1)) / 100.0
            new_val = min(1.0, round(context.brightness + delta, 2))
            return ActionSchema(action=ActionType.SET_BRIGHTNESS, value=new_val, reasoning=f"Regex increased brightness by {delta * 100}%")

        # Handle Absolute Brightness (e.g., "set brightness to 70%", "70%", "brightness 10%")
        absolute_match = re.search(r"(?:brightness\s+(?:to\s+)?|set\s+(?:it\s+)?to\s+)?(\d{1,3})\s*%", clean_text)
        if absolute_match and any(keyword in clean_text for keyword in ["bright", "set", "%", "to"]):
            val = float(absolute_match.group(1)) / 100.0
            val = max(0.0, min(1.0, val))
            return ActionSchema(action=ActionType.SET_BRIGHTNESS, value=val, reasoning="Regex matched absolute brightness")

        # Handle Turn On (supports "turn on", "turn it on", "switch on", "turn the light on")
        if re.search(r"\b(?:turn|switch|power)\s+(?:the\s+light\s+|it\s+)?on\b", clean_text) or re.search(r"\blights?\s+on\b", clean_text):
            return ActionSchema(action=ActionType.TURN_ON, reasoning="Regex matched turn on pattern")

        # Handle Turn Off (supports "turn off", "turn it off", "switch off", "turn the light off")
        if re.search(r"\b(?:turn|switch|power)\s+(?:the\s+light\s+|it\s+)?off\b", clean_text) or re.search(r"\blights?\s+off\b", clean_text):
            return ActionSchema(action=ActionType.TURN_OFF, reasoning="Regex matched turn off pattern")

        return ActionSchema(action=ActionType.UNKNOWN, reasoning="Regex could not determine intent")

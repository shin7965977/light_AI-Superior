from abc import ABC, abstractmethod

from src.ports.action_schema import ActionSchema, BulbContext


class BaseParser(ABC):
    """Abstract interface for natural language intent parsers."""

    @abstractmethod
    async def parse(self, text: str, context: BulbContext) -> ActionSchema:
        """Parses natural language user input given the current bulb state context."""

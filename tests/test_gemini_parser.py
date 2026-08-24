from unittest.mock import MagicMock, patch

import pytest

from src.adapters.gemini_parser import GeminiParser
from src.adapters.regex_parser import RegexParser
from src.ports.action_schema import ActionSchema, ActionType, BulbContext


@pytest.mark.asyncio
async def test_gemini_parser_missing_api_key_fallbacks_to_regex():
    with patch("src.adapters.gemini_parser.get_api_key", return_value=None):
        fallback_mock = MagicMock(spec=RegexParser)
        fallback_mock.parse.return_value = ActionSchema(action=ActionType.TURN_ON)

        parser = GeminiParser(fallback_parser=fallback_mock)
        ctx = BulbContext(is_on=False, brightness=0.5)

        res = await parser.parse("turn on", ctx)
        assert res.action == ActionType.TURN_ON
        fallback_mock.parse.assert_called_once_with("turn on", ctx)


@pytest.mark.asyncio
async def test_gemini_parser_api_exception_fallbacks_to_regex():
    with (
        patch("src.adapters.gemini_parser.get_api_key", return_value="fake-api-key"),
        patch("google.genai.Client", side_effect=Exception("API connection timeout")),
    ):
        fallback_mock = MagicMock(spec=RegexParser)
        fallback_mock.parse.return_value = ActionSchema(action=ActionType.TURN_OFF)

        parser = GeminiParser(fallback_parser=fallback_mock)
        ctx = BulbContext(is_on=True, brightness=0.5)

        res = await parser.parse("turn off", ctx)
        assert res.action == ActionType.TURN_OFF
        fallback_mock.parse.assert_called_once_with("turn off", ctx)


@pytest.mark.asyncio
async def test_gemini_parser_successful_structured_output():
    mock_action = ActionSchema(action=ActionType.SET_BRIGHTNESS, value=0.75, reasoning="dimmed")
    mock_response = MagicMock()
    mock_response.parsed = mock_action

    with (
        patch("src.adapters.gemini_parser.get_api_key", return_value="fake-api-key"),
        patch("google.genai.Client") as mock_client_cls,
    ):
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_response
        mock_client_cls.return_value = mock_client

        parser = GeminiParser()
        ctx = BulbContext(is_on=True, brightness=1.0)

        res = await parser.parse("set brightness to 75%", ctx)
        assert res.action == ActionType.SET_BRIGHTNESS
        assert res.value == 0.75


@pytest.mark.asyncio
async def test_gemini_parser_clarification_output():
    mock_action = ActionSchema(
        action=ActionType.CLARIFY,
        clarification_prompt="Did you mean to turn on or adjust brightness?",
        clarification_options=["Turn on", "Set to 50%"],
    )
    mock_response = MagicMock()
    mock_response.parsed = mock_action

    with (
        patch("src.adapters.gemini_parser.get_api_key", return_value="fake-api-key"),
        patch("google.genai.Client") as mock_client_cls,
    ):
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = mock_response
        mock_client_cls.return_value = mock_client

        parser = GeminiParser()
        ctx = BulbContext(is_on=False, brightness=0.0)

        res = await parser.parse("make it light", ctx)
        assert res.action == ActionType.CLARIFY
        assert res.clarification_prompt == "Did you mean to turn on or adjust brightness?"
        assert res.clarification_options == ["Turn on", "Set to 50%"]

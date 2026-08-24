import pytest

from src.adapters.regex_parser import RegexParser
from src.ports.action_schema import ActionType, BulbContext


@pytest.mark.asyncio
async def test_regex_turn_on():
    parser = RegexParser()
    ctx = BulbContext(is_on=False, brightness=0.5)

    res1 = await parser.parse("Please turn the light on", ctx)
    assert res1.action == ActionType.TURN_ON

    res2 = await parser.parse("switch on", ctx)
    assert res2.action == ActionType.TURN_ON


@pytest.mark.asyncio
async def test_regex_turn_off():
    parser = RegexParser()
    ctx = BulbContext(is_on=True, brightness=0.5)

    res1 = await parser.parse("Now please turn it off", ctx)
    assert res1.action == ActionType.TURN_OFF

    res2 = await parser.parse("turn off the light", ctx)
    assert res2.action == ActionType.TURN_OFF


@pytest.mark.asyncio
async def test_regex_toggle():
    parser = RegexParser()
    res_on = await parser.parse("Toggle the light", BulbContext(is_on=False, brightness=0.5))
    assert res_on.action == ActionType.TURN_ON

    res_off = await parser.parse("Toggle the light", BulbContext(is_on=True, brightness=0.5))
    assert res_off.action == ActionType.TURN_OFF


@pytest.mark.asyncio
async def test_regex_absolute_brightness():
    parser = RegexParser()
    ctx = BulbContext(is_on=True, brightness=0.5)

    res1 = await parser.parse("Please set the brightness to 70%", ctx)
    assert res1.action == ActionType.SET_BRIGHTNESS
    assert res1.value == 0.7

    res2 = await parser.parse("Now set it to 10% instead of 70%", ctx)
    assert res2.action == ActionType.SET_BRIGHTNESS
    assert res2.value == 0.10


@pytest.mark.asyncio
async def test_regex_relative_brightness():
    parser = RegexParser()
    ctx = BulbContext(is_on=True, brightness=0.8)

    res_dim = await parser.parse("Reduce the brightness by 20%", ctx)
    assert res_dim.action == ActionType.SET_BRIGHTNESS
    assert res_dim.value == 0.6

    res_boost = await parser.parse("Increase brightness by 10%", ctx)
    assert res_boost.action == ActionType.SET_BRIGHTNESS
    assert res_boost.value == 0.9


@pytest.mark.asyncio
async def test_regex_compound_negation():
    parser = RegexParser()
    ctx = BulbContext(is_on=False, brightness=0.5)

    res = await parser.parse("Switch it back on instead of off", ctx)
    assert res.action == ActionType.TURN_ON


@pytest.mark.asyncio
async def test_regex_clarification_disambiguation():
    parser = RegexParser()
    ctx = BulbContext(is_on=False, brightness=0.5)

    # Incomplete command: "light"
    res1 = await parser.parse("light", ctx)
    assert res1.action == ActionType.CLARIFY
    assert res1.clarification_prompt is not None
    assert len(res1.clarification_options) >= 2

    # Isolated number without %: "5"
    res_num = await parser.parse("5", ctx)
    assert res_num.action == ActionType.CLARIFY
    assert "5" in res_num.clarification_prompt
    assert any("5%" in opt for opt in res_num.clarification_options)

    # Incomplete percentage: "20%"
    res2 = await parser.parse("20%", ctx)
    assert res2.action == ActionType.CLARIFY
    assert "20%" in res2.clarification_prompt

    # Incomplete verb: "turn"
    res3 = await parser.parse("turn", ctx)
    assert res3.action == ActionType.CLARIFY

    # Typo: "trun on"
    res_typo = await parser.parse("trun on", ctx)
    assert res_typo.action == ActionType.CLARIFY


@pytest.mark.asyncio
async def test_regex_unknown_clarification():
    parser = RegexParser()
    ctx = BulbContext(is_on=False, brightness=0.5)

    # Broad clarification fallback for unrecognized commands
    res = await parser.parse("What is the weather today?", ctx)
    assert res.action == ActionType.CLARIFY
    assert "What is the weather today?" in res.clarification_prompt

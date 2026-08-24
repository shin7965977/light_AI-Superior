import pytest

from light_bulb import LightBulb
from src.adapters.regex_parser import RegexParser
from src.interface.repl import LightBulbCLI


@pytest.mark.asyncio
async def test_e2e_turn_on_flow():
    bulb = LightBulb()
    parser = RegexParser()
    cli = LightBulbCLI(bulb=bulb, parser=parser)

    # Initial state
    assert bulb.is_on is False

    # Execute action Turn On
    action = await parser.parse("Please turn the light on", cli.get_context())
    await cli.execute_action(action)

    assert bulb.is_on is True


@pytest.mark.asyncio
async def test_e2e_relative_dimming_flow():
    bulb = LightBulb()
    bulb.is_on = True
    bulb.brightness = 0.80

    parser = RegexParser()
    cli = LightBulbCLI(bulb=bulb, parser=parser)

    action = await parser.parse("Reduce the brightness by 20%", cli.get_context())
    await cli.execute_action(action)

    assert bulb.brightness == 0.60

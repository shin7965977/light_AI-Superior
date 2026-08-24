from light_bulb import LightBulb


def test_initial_state():
    bulb = LightBulb()
    assert bulb.is_on is False
    assert bulb.brightness == 1.0


def test_turn_on(capsys):
    bulb = LightBulb()
    bulb.turn_on()
    assert bulb.is_on is True
    captured = capsys.readouterr()
    assert "Light Bulb switched ON" in captured.out


def test_turn_off(capsys):
    bulb = LightBulb()
    bulb.turn_on()
    bulb.turn_off()
    assert bulb.is_on is False
    captured = capsys.readouterr()
    assert "Light Bulb switched OFF" in captured.out


def test_set_brightness(capsys):
    bulb = LightBulb()
    bulb.set_brightness(0.7)
    assert bulb.brightness == 0.7
    captured = capsys.readouterr()
    assert "Light Bulb brightness set to 70%" in captured.out

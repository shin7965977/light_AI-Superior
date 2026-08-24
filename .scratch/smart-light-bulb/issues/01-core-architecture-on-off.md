# 01: Core Architecture & Base On/Off Command

**What to build:** An initial end-to-end tracer bullet implementing the layered Clean Architecture skeleton. Users can run the CLI, see an initial ANSI light bulb displayed in dark gray (OFF state), enter basic natural language commands like "turn on" and "turn off", and observe the light bulb immediately update its visual state and print the corresponding confirmation.

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

- [ ] Domain entity `LightBulb` exists with state encapsulation (`is_on`, `brightness`).
- [ ] Application/Port layer defines `ActionSchema` and `BaseParser` interface.
- [ ] Interface layer runs an async CLI loop rendering the ANSI light bulb with `rich` and non-blocking input with `prompt_toolkit`.
- [ ] Entering "turn on" switches the bulb state to ON and prints "Light Bulb switched ON".
- [ ] Entering "turn off" switches the bulb state to OFF and prints "Light Bulb switched OFF".
- [ ] Automated unit test suite passes verifying domain state changes and command execution.

# Specification: Natural Language Smart Light Bulb CLI

## Problem Statement

Users need an intuitive, natural language command-line interface to interact with and control a virtual light bulb without having to memorize programming method signatures, parameter types, or rigid command-line syntax. Additionally, users require a smooth onboarding experience that handles API key configuration seamlessly, provides clear real-time visual feedback of the bulb's state, and handles both simple and context-dependent instructions efficiently.

## Solution

An interactive, asynchronous CLI application built with Clean Architecture that allows users to control a virtual light bulb via natural language:
- **Onboarding & Configuration**: Automatically checks for `GEMINI_API_KEY`; if missing, prompts the user interactively and saves the key into a local `.env` file for persistent use.
- **Visual Feedback**: Displays a centered ASCII/ANSI light bulb rendered with `rich` that dynamically reflects the power status and brightness level (defaulting to 0% dark gray), paired with an asynchronous non-blocking input prompt using `prompt_toolkit`.
- **Dual-Layer Parsing Strategy**:
  - **Primary Semantic Parser (`GeminiParser`)**: Powered by **`gemini-3.5-flash`** using structured outputs (Pydantic schema) and injecting current bulb state (`is_on`, `brightness`) context to resolve all natural language commands, including simple, relative adjustments ("dim by 20%"), state flips ("toggle"), and compound sentences ("switch it back on instead of off").
  - **Resilience Fallback (`RegexParser`)**: Serves as an offline/error fallback to locally resolve standard commands if the Gemini API is unreachable or the network is disconnected.
- **Observability**: Background structured logging (`structlog`) writing latency and execution metrics to `app.log` without disrupting the terminal UI.
- **Quality & Delivery**: Comprehensive unit tests with mocked LLM calls for sub-second offline verification, multi-stage Docker containerization, and automated GitHub Actions CI.

## User Stories

1. As a user, I want the CLI to prompt me for my Gemini API key if it is not configured, so that I can set up authentication directly inside the terminal.
2. As a user, I want my entered Gemini API key saved to a local `.env` file, so that I do not need to re-type it on subsequent runs.
3. As a user, I want to see an ASCII/ANSI light bulb in the terminal, so that I receive immediate visual feedback on the state of the bulb.
4. As a user, I want the initial bulb state to be OFF with 0% brightness (rendered dark gray), so that I know the system starts from a safe default.
5. As a user, I want to switch the light ON using natural language commands (e.g., "Please turn the light on"), so that the bulb powers on effortlessly.
6. As a user, I want to switch the light OFF using natural language commands (e.g., "Now please turn it off"), so that the bulb powers down cleanly.
7. As a user, I want to toggle the light state (e.g., "Toggle the light"), so that it switches state based on whether it is currently ON or OFF.
8. As a user, I want to set absolute brightness levels (e.g., "Please set the brightness to 70%"), so that I can specify an exact illumination level.
9. As a user, I want to make relative brightness adjustments (e.g., "Reduce the brightness by 20%"), so that the system calculates the new brightness based on the current value.
10. As a user, I want the system to handle semantic corrections and compound sentences (e.g., "Switch it back on instead of off"), so that it resolves to the correct intended action.
11. As a user, I want all natural language commands to be processed by Gemini 3.5 Flash by default, with automatic fallback to local regex parsing if offline, so that I get maximum semantic intelligence with high availability.
12. As a user, I want invalid or unrelated commands (e.g., "What's the weather today?") to be gracefully acknowledged with an informative message without crashing the CLI.
13. As an engineer, I want structured execution logs and latency metrics written to `app.log`, so that I can monitor and debug parsing decisions without polluting the interactive CLI view.
14. As an evaluator, I want to run the entire system inside a multi-stage Docker container, so that I can test the solution in an isolated, reproducible environment.
15. As an evaluator, I want an automated CI pipeline running linter (`ruff`), type checker (`mypy`), and test suite (`pytest`), so that code standards and test coverage are verified automatically.

## Implementation Decisions

1. **Layered Clean Architecture**:
   - **Domain Layer**: The `LightBulb` entity maintaining state (`is_on: bool`, `brightness: float`) and core methods (`turn_on()`, `turn_off()`, `set_brightness()`).
   - **Application / Ports Layer**: Defines `ActionSchema` (Pydantic model with `ActionType` enum: `TURN_ON`, `TURN_OFF`, `SET_BRIGHTNESS`, `UNKNOWN`, and normalized `value: Optional[float]`) and `BaseParser` abstract base class.
   - **Adapter Layer**: Implements `GeminiParser` (Primary parser utilizing `gemini-3.5-flash` with Structured Outputs / response schemas and state context injection) and `RegexParser` (Offline and error fallback parser).
   - **Interface Layer**: Asynchronous REPL running on `asyncio`, utilizing `prompt_toolkit` for non-blocking command input and `rich` for ANSI bulb rendering.
2. **Parser Precedence & Resilience (Gemini-First)**:
   - Every user input is dispatched to `GeminiParser` (using `gemini-3.5-flash`) by default with state context (`is_on`, `brightness`) for full natural language comprehension.
   - If an API timeout, rate limit, authentication failure, or network error occurs, the system automatically falls back to `RegexParser` to preserve baseline offline functionality.
3. **Model Selection**:
   - Default model configured as `gemini-3.5-flash` (configurable via `GEMINI_MODEL` environment variable in `.env`).
4. **Event-Driven UI Update**:
   - State mutations on `LightBulb` trigger a notification callback to re-render the ANSI art and update status messages.
5. **Observability & Logging**:
   - `structlog` configured to output JSON logs to `app.log` capturing timestamp, input text, parser used (`regex` vs `gemini`), latency in milliseconds, and action executed.

## Testing Decisions

- **Testing Seams**:
  1. **Domain Logic Seam**: Direct verification of `LightBulb` state transitions and boundary clipping (`0.0 <= brightness <= 1.0`).
  2. **Parser Seams**:
     - `RegexParser`: Verifying fast-path match correctness across basic commands.
     - `GeminiParser`: Mocking LLM API responses via `unittest.mock` to verify prompt construction, schema deserialization, and state-dependent logic (e.g., relative dimming, toggling).
  3. **End-to-End Orchestrator Seam**: Testing command pipeline from input string to bulb state update.
- **Test Execution Rules**:
  - All unit tests must run offline without requiring network access or a live `GEMINI_API_KEY`.
  - Tests must execute in sub-second times with 100% deterministic results.

## Out of Scope

- Physical IoT hardware communication protocols (e.g., Zigbee, Z-Wave, MQTT, Home Assistant API).
- Multi-user authentication or multi-tenant device registry.
- Web or mobile graphical user interfaces (strictly CLI scope).
- Persistent external database storage (state is ephemeral during the CLI session).

## Further Notes

- Full architectural decisions, Double Diamond development reasoning, and evaluation instructions will be documented in `SOLUTION.md`.

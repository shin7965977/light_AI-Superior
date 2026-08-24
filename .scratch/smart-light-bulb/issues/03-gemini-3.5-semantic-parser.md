# 03: Gemini 3.5 Flash Semantic Parser Integration

**What to build:** Primary semantic intent extraction using `gemini-3.5-flash` via the official `google-genai` SDK with Structured Outputs. The parser injects the light bulb's current state context (`is_on`, `brightness`) into the prompt to resolve complex instructions, compound sentences (e.g., "Switch it back on instead of off"), and state toggling ("Toggle the light").

**Blocked by:** 02: API Key Onboarding & Environment Persistence

**Status:** ready-for-agent

- [ ] `GeminiParser` integrates with `gemini-3.5-flash` (configurable via `GEMINI_MODEL`).
- [ ] Uses Structured Outputs adhering strictly to `ActionSchema` (Pydantic).
- [ ] Passes current light bulb state context (`is_on`, `brightness`) with every query.
- [ ] Correctly resolves "Toggle the light" based on current state (turns ON if OFF, turns OFF if ON).
- [ ] Correctly resolves compound/negation commands like "Switch it back on instead of off".
- [ ] Unit tests verify parser prompt assembly and intent mapping using mocked LLM responses (`unittest.mock`) without real network calls.

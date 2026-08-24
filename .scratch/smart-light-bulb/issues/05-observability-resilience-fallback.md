# 05: Observability, Error Handling & Fallback Routing

**What to build:** Comprehensive observability and fault tolerance. In the background, `structlog` writes structured logs to `app.log` recording parsing method, latency, and token consumption without disturbing the UI. If the user enters unrelated/invalid commands (e.g., "What's the weather?"), the system responds gracefully. If the Gemini API fails or disconnects, the system automatically falls back to `RegexParser`.

**Blocked by:** 04: Brightness & Relative Adjustment Parsing

**Status:** done

- [x] `structlog` configured to write structured JSON/formatted logs to `app.log`.
- [x] Tracks request latency (ms), token usage, and parser routing decisions (`gemini` vs `regex_fallback`).
- [x] Handles UNKNOWN / invalid intents (e.g., "What's the weather today?") with a helpful message without crashing.
- [x] Automatic fallback to `RegexParser` when Gemini API fails, timeouts, or hits rate limits.
- [x] Unit tests verify fallback triggering upon simulated API failures.

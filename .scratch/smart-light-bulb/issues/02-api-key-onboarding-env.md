# 02: API Key Onboarding & Environment Persistence

**What to build:** An interactive onboarding experience that checks for the `GEMINI_API_KEY` upon application startup. If the key is not present in the environment or `.env`, the CLI prompts the user to input/paste their Gemini API key, automatically saves it to a local `.env` file, and loads the environment without requiring a manual restart.

**Blocked by:** 01: Core Architecture & Base On/Off Command

**Status:** done

- [x] Startup routine checks environment variables and `.env` for `GEMINI_API_KEY`.
- [x] If missing, prompts the user in the terminal: "Please enter your Gemini API Key: ".
- [x] Automatically creates or updates the local `.env` file with the provided key.
- [x] Environment configuration reloads dynamically so subsequent LLM calls have access to the key.
- [x] Unit tests verify that missing keys trigger the onboarding handler and `.env` persistence works as expected.

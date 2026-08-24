# 04: Brightness & Relative Adjustment Parsing

**What to build:** Full natural language control over light bulb brightness, including absolute values (e.g., "Set brightness to 70%") and relative percentage adjustments (e.g., "Dim by 20%", "Increase brightness by 15%"). The ANSI light bulb visually reflects brightness levels with graduated colors and illumination symbols.

**Blocked by:** 03: Gemini 3.5 Flash Semantic Parser Integration

**Status:** done

- [x] Parsing supports absolute brightness commands (e.g., "Set the brightness to 70%").
- [x] Parsing supports relative brightness calculations (e.g., current 0.8 dimming by 20% sets brightness to 0.6).
- [x] Safe numeric bounds enforcement ensuring brightness values always clip within `[0.0, 1.0]`.
- [x] ANSI light bulb renderer updates brightness dynamically with matching color intensities in terminal.
- [x] Unit tests cover absolute values, relative increments/decrements, and boundary conditions (e.g. setting 150% or -20%).

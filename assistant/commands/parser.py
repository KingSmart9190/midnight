from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class CommandIntent:
    name: str
    argument: str | None = None


class RuleBasedCommandParser:
    """Initial deterministic parser; can be replaced by NLP later."""

    def parse(self, text: str) -> Optional[CommandIntent]:
        normalized = text.strip().lower()

        if any(p in normalized for p in ["open browser", "launch browser"]):
            return CommandIntent(name="open_browser")
        if normalized.startswith("open file"):
            return CommandIntent(name="open_file", argument=normalized.removeprefix("open file").strip())
        if any(p in normalized for p in ["shutdown pc", "shutdown computer", "power off"]):
            return CommandIntent(name="shutdown_pc")
        if any(p in normalized for p in ["play music", "start music"]):
            return CommandIntent(name="play_music")
        if any(p in normalized for p in ["switch window", "next window"]):
            return CommandIntent(name="switch_window")
        if normalized.startswith("type text"):
            return CommandIntent(name="type_text", argument=normalized.removeprefix("type text").strip())

        return None

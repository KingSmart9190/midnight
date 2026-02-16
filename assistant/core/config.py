from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict
import json


@dataclass(slots=True)
class AssistantConfig:
    wake_word: str = "assistant"
    language: str = "en-US"
    speech_rate: int = 180
    listen_timeout: int = 3
    phrase_time_limit: int = 5
    gesture_camera_index: int = 0
    gesture_confidence: float = 0.6
    plugin_dir: str = "assistant/plugins"
    command_map: Dict[str, str] = field(default_factory=dict)

    @classmethod
    def load(cls, path: str | Path) -> "AssistantConfig":
        file_path = Path(path)
        if not file_path.exists():
            return cls()
        data: Dict[str, Any] = json.loads(file_path.read_text(encoding="utf-8"))
        return cls(**data)

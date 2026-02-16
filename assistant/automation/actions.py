from __future__ import annotations

import logging
import os
import platform
import subprocess
import webbrowser
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


class Action(Protocol):
    def execute(self) -> None: ...


@dataclass(slots=True)
class OpenBrowserAction:
    url: str = "https://www.google.com"

    def execute(self) -> None:
        webbrowser.open(self.url)


@dataclass(slots=True)
class OpenFileAction:
    file_path: str

    def execute(self) -> None:
        path = Path(self.file_path).expanduser()
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        if platform.system() == "Windows":
            os.startfile(path)  # type: ignore[attr-defined]
        elif platform.system() == "Darwin":
            subprocess.run(["open", str(path)], check=False)
        else:
            subprocess.run(["xdg-open", str(path)], check=False)


class ShutdownPCAction:
    def execute(self) -> None:
        system = platform.system()
        if system == "Windows":
            subprocess.run(["shutdown", "/s", "/t", "5"], check=False)
        elif system == "Darwin":
            subprocess.run(["osascript", "-e", 'tell app "System Events" to shut down'], check=False)
        else:
            subprocess.run(["shutdown", "-h", "+1"], check=False)


@dataclass(slots=True)
class PlayMusicAction:
    path: str = "~/Music"

    def execute(self) -> None:
        OpenFileAction(self.path).execute()


@dataclass(slots=True)
class SwitchWindowAction:
    logger: logging.Logger

    def execute(self) -> None:
        try:
            import pyautogui

            if platform.system() == "Darwin":
                pyautogui.hotkey("command", "tab")
            else:
                pyautogui.hotkey("alt", "tab")
        except Exception as exc:  # noqa: BLE001
            self.logger.warning("Unable to switch window: %s", exc)


@dataclass(slots=True)
class TypeTextAction:
    text: str
    logger: logging.Logger

    def execute(self) -> None:
        try:
            import pyautogui

            pyautogui.write(self.text)
        except Exception as exc:  # noqa: BLE001
            self.logger.warning("Unable to type text: %s", exc)

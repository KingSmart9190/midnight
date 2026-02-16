from __future__ import annotations

import importlib.util
import logging
from pathlib import Path
from typing import Callable, Dict, List

from assistant.automation.actions import Action


class AutomationEngine:
    """Executes single actions and chained action pipelines."""

    def __init__(self) -> None:
        self._logger = logging.getLogger(self.__class__.__name__)
        self._pipelines: Dict[str, List[Action]] = {}

    def execute(self, action: Action) -> None:
        self._logger.info("Executing action %s", action.__class__.__name__)
        action.execute()

    def register_pipeline(self, name: str, actions: List[Action]) -> None:
        self._pipelines[name] = actions

    def run_pipeline(self, name: str) -> bool:
        actions = self._pipelines.get(name)
        if not actions:
            return False
        for action in actions:
            self.execute(action)
        return True

    def load_plugins(self, plugin_dir: str) -> Dict[str, Callable[[], None]]:
        hooks: Dict[str, Callable[[], None]] = {}
        root = Path(plugin_dir)
        if not root.exists():
            return hooks

        for file in root.glob("*.py"):
            if file.name.startswith("__"):
                continue
            spec = importlib.util.spec_from_file_location(file.stem, file)
            if not spec or not spec.loader:
                continue
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            plugin_hooks = getattr(module, "PLUGIN_HOOKS", {})
            if isinstance(plugin_hooks, dict):
                hooks.update(plugin_hooks)
        return hooks

from __future__ import annotations

import logging
from typing import Callable, Dict, Iterable

from assistant.commands.parser import CommandIntent


CommandHandler = Callable[[CommandIntent], None]


class CommandRouter:
    def __init__(self) -> None:
        self._handlers: Dict[str, CommandHandler] = {}
        self._logger = logging.getLogger(self.__class__.__name__)

    def register(self, name: str, handler: CommandHandler) -> None:
        self._handlers[name] = handler

    def bulk_register(self, items: Iterable[tuple[str, CommandHandler]]) -> None:
        for name, handler in items:
            self.register(name, handler)

    def dispatch(self, intent: CommandIntent) -> bool:
        handler = self._handlers.get(intent.name)
        if not handler:
            self._logger.warning("No handler registered for intent=%s", intent.name)
            return False
        handler(intent)
        return True

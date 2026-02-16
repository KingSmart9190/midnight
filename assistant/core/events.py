from __future__ import annotations

import logging
from collections import defaultdict
from dataclasses import dataclass, field
from queue import Empty, Queue
from threading import Event, Thread
from time import perf_counter
from typing import Any, Callable, Dict, List


@dataclass(slots=True)
class AssistantEvent:
    """A typed event moving through the assistant system."""

    event_type: str
    payload: Dict[str, Any] = field(default_factory=dict)
    source: str = "unknown"
    ts: float = field(default_factory=perf_counter)


EventHandler = Callable[[AssistantEvent], None]


class EventBus:
    """Thread-safe event bus with async dispatch."""

    def __init__(self) -> None:
        self._handlers: Dict[str, List[EventHandler]] = defaultdict(list)
        self._queue: Queue[AssistantEvent] = Queue()
        self._stop = Event()
        self._worker: Thread | None = None
        self._logger = logging.getLogger(self.__class__.__name__)

    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        self._handlers[event_type].append(handler)

    def publish(self, event: AssistantEvent) -> None:
        self._queue.put(event)

    def start(self) -> None:
        if self._worker and self._worker.is_alive():
            return
        self._stop.clear()
        self._worker = Thread(target=self._run, name="event-bus", daemon=True)
        self._worker.start()

    def stop(self) -> None:
        self._stop.set()
        if self._worker:
            self._worker.join(timeout=1.0)

    def _run(self) -> None:
        while not self._stop.is_set():
            try:
                event = self._queue.get(timeout=0.1)
            except Empty:
                continue

            handlers = self._handlers.get(event.event_type, []) + self._handlers.get("*", [])
            for handler in handlers:
                try:
                    handler(event)
                except Exception as exc:  # noqa: BLE001
                    self._logger.exception("event handler failure: %s", exc)

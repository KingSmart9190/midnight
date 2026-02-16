from __future__ import annotations

import logging
from threading import Event, Thread

from assistant.core.events import AssistantEvent, EventBus


class VoiceInputService:
    """Continuously captures microphone input and emits transcribed text events."""

    def __init__(self, bus: EventBus, language: str = "en-US", timeout: int = 3, phrase_time_limit: int = 5) -> None:
        self._bus = bus
        self._language = language
        self._timeout = timeout
        self._phrase_time_limit = phrase_time_limit
        self._stop = Event()
        self._thread: Thread | None = None
        self._logger = logging.getLogger(self.__class__.__name__)

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = Thread(target=self._run, name="voice-input", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=1)

    def _run(self) -> None:
        try:
            import speech_recognition as sr
        except Exception as exc:  # noqa: BLE001
            self._logger.error("SpeechRecognition unavailable: %s", exc)
            return

        recognizer = sr.Recognizer()
        mic = sr.Microphone()

        with mic as source:
            recognizer.adjust_for_ambient_noise(source)

        while not self._stop.is_set():
            try:
                with mic as source:
                    audio = recognizer.listen(source, timeout=self._timeout, phrase_time_limit=self._phrase_time_limit)
                text = recognizer.recognize_google(audio, language=self._language)
                self._bus.publish(AssistantEvent(event_type="voice.text", payload={"text": text}, source="voice"))
            except Exception as exc:  # noqa: BLE001
                self._logger.debug("voice loop: %s", exc)

from __future__ import annotations

import logging
from dataclasses import dataclass


@dataclass(slots=True)
class FeedbackMessage:
    title: str
    body: str


class FeedbackManager:
    def __init__(self, speech_rate: int = 180) -> None:
        self._logger = logging.getLogger(self.__class__.__name__)
        self._speech_engine = None
        self._init_speech(speech_rate)

    def _init_speech(self, speech_rate: int) -> None:
        try:
            import pyttsx3

            engine = pyttsx3.init()
            engine.setProperty("rate", speech_rate)
            self._speech_engine = engine
        except Exception as exc:  # noqa: BLE001
            self._logger.warning("Speech synthesis unavailable: %s", exc)

    def speak(self, text: str) -> None:
        self._logger.info("Assistant says: %s", text)
        if not self._speech_engine:
            return
        self._speech_engine.say(text)
        self._speech_engine.runAndWait()

    def notify(self, msg: FeedbackMessage) -> None:
        try:
            from plyer import notification

            notification.notify(title=msg.title, message=msg.body, timeout=3)
        except Exception as exc:  # noqa: BLE001
            self._logger.warning("Desktop notification unavailable: %s", exc)

    def publish_all(self, msg: FeedbackMessage) -> None:
        self.speak(msg.body)
        self.notify(msg)

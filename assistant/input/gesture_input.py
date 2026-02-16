from __future__ import annotations

import logging
from collections import deque
from threading import Event, Thread
from typing import Deque, Optional

from assistant.core.events import AssistantEvent, EventBus


class GestureInputService:
    """MediaPipe based hand gesture recognition service."""

    def __init__(self, bus: EventBus, camera_index: int = 0, min_confidence: float = 0.6) -> None:
        self._bus = bus
        self._camera_index = camera_index
        self._min_confidence = min_confidence
        self._thread: Thread | None = None
        self._stop = Event()
        self._logger = logging.getLogger(self.__class__.__name__)
        self._x_history: Deque[float] = deque(maxlen=6)

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = Thread(target=self._run, name="gesture-input", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=1)

    def _run(self) -> None:
        try:
            import cv2
            import mediapipe as mp
        except Exception as exc:  # noqa: BLE001
            self._logger.error("Gesture dependencies unavailable: %s", exc)
            return

        cap = cv2.VideoCapture(self._camera_index)
        mp_hands = mp.solutions.hands
        with mp_hands.Hands(min_detection_confidence=self._min_confidence, min_tracking_confidence=self._min_confidence) as hands:
            while not self._stop.is_set():
                ok, frame = cap.read()
                if not ok:
                    continue
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                result = hands.process(rgb)
                gesture = self._recognize(result)
                if gesture:
                    self._bus.publish(AssistantEvent(event_type="gesture.detected", payload={"gesture": gesture}, source="gesture"))
        cap.release()

    def _recognize(self, result: object) -> Optional[str]:
        multi_hand_landmarks = getattr(result, "multi_hand_landmarks", None)
        if not multi_hand_landmarks:
            return None

        hand = multi_hand_landmarks[0]
        landmarks = hand.landmark
        tip_ids = [4, 8, 12, 16, 20]

        fingers_up = []
        fingers_up.append(landmarks[4].x > landmarks[3].x)
        for tip in tip_ids[1:]:
            fingers_up.append(landmarks[tip].y < landmarks[tip - 2].y)

        index_x = landmarks[8].x
        self._x_history.append(index_x)
        if len(self._x_history) >= 5:
            delta = self._x_history[-1] - self._x_history[0]
            if delta > 0.20:
                self._x_history.clear()
                return "swipe_right"
            if delta < -0.20:
                self._x_history.clear()
                return "swipe_left"

        if all(fingers_up[1:]):
            return "open_palm"
        if not any(fingers_up[1:]):
            return "fist"
        if fingers_up[1] and not any(fingers_up[2:]):
            return "point"

        return None

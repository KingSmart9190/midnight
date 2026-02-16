from __future__ import annotations

import logging
from threading import Event

from assistant.automation.actions import (
    OpenBrowserAction,
    OpenFileAction,
    PlayMusicAction,
    ShutdownPCAction,
    SwitchWindowAction,
    TypeTextAction,
)
from assistant.automation.engine import AutomationEngine
from assistant.commands.parser import CommandIntent, RuleBasedCommandParser
from assistant.commands.router import CommandRouter
from assistant.core.config import AssistantConfig
from assistant.core.events import AssistantEvent, EventBus
from assistant.feedback.feedback import FeedbackManager, FeedbackMessage
from assistant.input.gesture_input import GestureInputService
from assistant.input.voice_input import VoiceInputService


class ServiceManager:
    def __init__(self, config: AssistantConfig) -> None:
        self.config = config
        self.bus = EventBus()
        self.parser = RuleBasedCommandParser()
        self.router = CommandRouter()
        self.automation = AutomationEngine()
        self.feedback = FeedbackManager(speech_rate=config.speech_rate)
        self.voice = VoiceInputService(
            self.bus,
            language=config.language,
            timeout=config.listen_timeout,
            phrase_time_limit=config.phrase_time_limit,
        )
        self.gesture = GestureInputService(
            self.bus,
            camera_index=config.gesture_camera_index,
            min_confidence=config.gesture_confidence,
        )
        self._stop = Event()
        self._logger = logging.getLogger(self.__class__.__name__)

    def configure(self) -> None:
        self.router.bulk_register(
            [
                ("open_browser", lambda _: self.automation.execute(OpenBrowserAction())),
                ("open_file", lambda intent: self.automation.execute(OpenFileAction(intent.argument or ""))),
                ("shutdown_pc", lambda _: self.automation.execute(ShutdownPCAction())),
                ("play_music", lambda _: self.automation.execute(PlayMusicAction())),
                ("switch_window", lambda _: self.automation.execute(SwitchWindowAction(self._logger))),
                ("type_text", lambda intent: self.automation.execute(TypeTextAction(intent.argument or "", self._logger))),
            ]
        )

        self.automation.register_pipeline(
            "summary_flow",
            [
                OpenFileAction("~/notes.txt"),
                TypeTextAction("Summarize my notes", self._logger),
            ],
        )

        plugins = self.automation.load_plugins(self.config.plugin_dir)
        for name, callback in plugins.items():
            self.router.register(name, lambda _, cb=callback: cb())

        self.bus.subscribe("voice.text", self._on_voice_text)
        self.bus.subscribe("gesture.detected", self._on_gesture)

    def start(self) -> None:
        self.configure()
        self.bus.start()
        self.voice.start()
        self.gesture.start()
        self.feedback.publish_all(FeedbackMessage("Assistant", "Multimodal assistant started."))

    def stop(self) -> None:
        self.voice.stop()
        self.gesture.stop()
        self.bus.stop()
        self.feedback.publish_all(FeedbackMessage("Assistant", "Assistant stopped."))

    def _on_voice_text(self, event: AssistantEvent) -> None:
        text = str(event.payload.get("text", ""))
        self._logger.info("voice> %s", text)
        intent = self.parser.parse(text)
        if not intent:
            self.feedback.speak("I did not understand that command.")
            return

        success = self.router.dispatch(intent)
        if success:
            self.feedback.speak(f"Done: {intent.name}")
        else:
            self.feedback.speak("That command is not supported yet.")

    def _on_gesture(self, event: AssistantEvent) -> None:
        gesture = str(event.payload.get("gesture"))
        self._logger.info("gesture> %s", gesture)
        gesture_to_intent = {
            "swipe_left": "switch_window",
            "swipe_right": "switch_window",
            "open_palm": "open_browser",
            "fist": "play_music",
            "point": "type_text",
        }
        intent_name = gesture_to_intent.get(gesture)
        if not intent_name:
            return

        argument = "gesture triggered text" if intent_name == "type_text" else None
        success = self.router.dispatch(CommandIntent(name=intent_name, argument=argument))
        if success:
            self.feedback.notify(FeedbackMessage("Gesture", f"Executed {intent_name} from {gesture}"))

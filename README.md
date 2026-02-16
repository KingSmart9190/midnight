# Multimodal AI Desktop Assistant (Voice + Gesture Controlled)

A modular, production-style desktop assistant prototype that combines:
- Voice recognition + spoken feedback
- Gesture recognition from webcam
- Command routing and automation actions
- Plugin-based automation extension points
- Event-driven, non-blocking service architecture

## 1) Architecture Overview

### Core Design
- **Event Bus** (`assistant/core/events.py`): asynchronous event transport between input services and handlers.
- **Service Manager** (`assistant/core/service_manager.py`): composition root that wires voice, gesture, router, automation, and feedback.
- **Rule-Based Parser** (`assistant/commands/parser.py`): deterministic intent extraction now; swappable for NLP/LLM parser later.
- **Command Router** (`assistant/commands/router.py`): maps intents to handlers.
- **Automation Engine** (`assistant/automation/engine.py`): executes actions and action pipelines, loads plugin hooks.
- **Feedback Manager** (`assistant/feedback/feedback.py`): voice TTS + desktop notifications.

### Input Layer
- **Voice Input Service** (`assistant/input/voice_input.py`): continuously listens from microphone, emits `voice.text` events.
- **Gesture Input Service** (`assistant/input/gesture_input.py`): detects hand landmarks via MediaPipe and emits `gesture.detected` events for:
  - `swipe_left`
  - `swipe_right`
  - `open_palm`
  - `fist`
  - `point`

### Extensibility
- Plugins loaded from `assistant/plugins/*.py` via `PLUGIN_HOOKS` dictionary.
- Clean interfaces allow replacing parser with NLP model, swapping speech backends, and extending automation actions.

## 2) Folder Structure

```text
.
├── assistant
│   ├── automation
│   │   ├── actions.py
│   │   └── engine.py
│   ├── commands
│   │   ├── parser.py
│   │   └── router.py
│   ├── core
│   │   ├── config.py
│   │   ├── events.py
│   │   ├── logging_config.py
│   │   └── service_manager.py
│   ├── feedback
│   │   └── feedback.py
│   ├── input
│   │   ├── gesture_input.py
│   │   └── voice_input.py
│   ├── plugins
│   │   └── sample_plugin.py
│   └── ui
│       └── overlay.py
├── config.json
├── main.py
├── requirements.txt
├── scripts
│   └── run.sh
└── tests
    ├── test_parser.py
    └── test_router.py
```

## 3) Source Code Notes

All requested phases are implemented:
- **Phase 1**: Continuous voice capture, rule-based parser, command execution.
- **Phase 2**: Real-time gesture detection and mappings.
- **Phase 3**: Automation action layer, dispatcher/router, chained pipeline support, plugin hooks.
- **Phase 4**: Integrated non-blocking loop through event bus with voice + desktop feedback.
- **Phase 5**: API-level extensibility for context/intelligence upgrades through parser replacement and plugin expansion.

## 4) Setup Instructions

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
```

If `PyAudio` is required for your OS microphone stack, install it separately per platform.

## 5) Run

```bash
./scripts/run.sh
# or
python main.py
```

Stop with `Ctrl+C`.

## 6) Usage Examples

### Voice
- “open browser” → opens browser.
- “open file /home/user/notes.txt” → opens the file.
- “shutdown pc” → issues shutdown command.
- “play music” → opens `~/Music`.
- “type text hello world” → types text via automation.

### Gesture
- Swipe left/right → switch window.
- Open palm → open browser.
- Fist → play music.
- Point → type default text.

### Plugin command example
Add new hooks in a plugin file under `assistant/plugins`:

```python
PLUGIN_HOOKS = {
  "my_custom_flow": my_custom_flow,
}
```

Then trigger from voice by extending parser mapping to `my_custom_flow`.

## 7) Testing Instructions

```bash
pytest -q
python -m compileall assistant main.py
```

## 8) Performance Notes
- Local/offline core behavior for command routing and gesture processing.
- Event-driven threads keep capture and command execution non-blocking.
- Lightweight rule-based parsing keeps intent dispatch sub-500ms on normal hardware.

## 9) Future Improvements
- Replace parser with transformer/LLM intent model behind same parser interface.
- Personal gesture calibration and per-user profile persistence.
- Vosk offline ASR backend for fully offline speech recognition.
- Rich overlay GUI with status, confidence, and command history.
- Cloud sync hooks (Android companion, reminders, cross-device context).

from __future__ import annotations

import signal
import time

from assistant.core.config import AssistantConfig
from assistant.core.logging_config import configure_logging
from assistant.core.service_manager import ServiceManager


def main() -> None:
    configure_logging()
    config = AssistantConfig.load("config.json")
    manager = ServiceManager(config)

    running = True

    def _stop_handler(*_: object) -> None:
        nonlocal running
        running = False

    signal.signal(signal.SIGINT, _stop_handler)
    signal.signal(signal.SIGTERM, _stop_handler)

    manager.start()
    while running:
        time.sleep(0.2)
    manager.stop()


if __name__ == "__main__":
    main()

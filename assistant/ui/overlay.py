from __future__ import annotations

import threading
import tkinter as tk


class Overlay:
    """Small optional always-on-top status overlay."""

    def __init__(self) -> None:
        self._root = None
        self._label = None
        self._thread = None

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self) -> None:
        self._root = tk.Tk()
        self._root.title("Assistant")
        self._root.geometry("240x70+30+30")
        self._root.attributes("-topmost", True)
        self._label = tk.Label(self._root, text="Assistant Ready", font=("Arial", 12))
        self._label.pack(fill=tk.BOTH, expand=True)
        self._root.mainloop()

    def set_status(self, text: str) -> None:
        if self._label:
            self._label.config(text=text)

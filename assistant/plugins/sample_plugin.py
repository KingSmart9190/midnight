"""Example automation plugin hooks."""


def open_school_system() -> None:
    import webbrowser

    webbrowser.open("https://example.com/school-system")


PLUGIN_HOOKS = {
    "open_school_system": open_school_system,
}

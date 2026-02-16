from assistant.commands.parser import CommandIntent
from assistant.commands.router import CommandRouter


def test_dispatch_registered_handler() -> None:
    router = CommandRouter()
    called = {"ok": False}

    def handler(_: CommandIntent) -> None:
        called["ok"] = True

    router.register("open_browser", handler)

    assert router.dispatch(CommandIntent(name="open_browser"))
    assert called["ok"]


def test_dispatch_missing_handler() -> None:
    router = CommandRouter()
    assert not router.dispatch(CommandIntent(name="missing"))

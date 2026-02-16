from assistant.commands.parser import RuleBasedCommandParser


def test_open_browser_intent() -> None:
    parser = RuleBasedCommandParser()
    intent = parser.parse("open browser")
    assert intent is not None
    assert intent.name == "open_browser"


def test_open_file_argument() -> None:
    parser = RuleBasedCommandParser()
    intent = parser.parse("open file /tmp/a.txt")
    assert intent is not None
    assert intent.name == "open_file"
    assert intent.argument == "/tmp/a.txt"

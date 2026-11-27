import subprocess
import sys
from types import SimpleNamespace

from clioraOps_cli.web_interface import WebInterface


def test_import_does_not_require_gradio():
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import sys; sys.modules['gradio'] = None; "
                "from clioraOps_cli.web_interface import WebInterface"
            ),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr


def test_web_interface_blocks_explicit_execution(monkeypatch):
    route_calls = []
    conversation_calls = []

    class FakeCommandRouter:
        def is_execute_request(self, message):
            return message.lstrip().lower().startswith("execute ")

        def route(self, message):
            route_calls.append(message)

    class FakeConversation:
        def is_conversational_input(self, message):
            return True

        def handle_conversation(self, message):
            conversation_calls.append(message)
            return "Conversation response"

    fake_app = SimpleNamespace(
        command_router=FakeCommandRouter(),
        session=SimpleNamespace(conversation=FakeConversation()),
    )
    web = WebInterface.__new__(WebInterface)
    web.app_beginner = fake_app
    web.app_architect = fake_app

    _, history = web.chat("execute docker ps", "Beginner", [])

    assert route_calls == []
    assert conversation_calls == []
    assert len(history) == 1
    assert "only in the interactive CLI" in history[0][1]

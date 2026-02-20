import pytest
from unittest.mock import MagicMock, patch
from clioraOps_cli.core.app import ClioraOpsApp
from clioraOps_cli.core.modes import Mode


class TestClioraOpsAppInitialization:
    """Test ClioraOpsApp initialization."""

    @patch("clioraOps_cli.core.app.create_ai_client")
    @patch("clioraOps_cli.core.app.SessionManager")
    @patch("clioraOps_cli.core.app.CommandRouter")
    def test_app_init_beginner_mode(self, mock_router, mock_session, mock_create_ai):
        mock_ai_instance = MagicMock()
        mock_create_ai.return_value = mock_ai_instance

        app = ClioraOpsApp(Mode.BEGINNER)

        assert app.mode == Mode.BEGINNER
        assert app.ai is not None
        mock_create_ai.assert_called_once_with(mode=Mode.BEGINNER)

    @patch("clioraOps_cli.core.app.create_ai_client")
    @patch("clioraOps_cli.core.app.SessionManager")
    @patch("clioraOps_cli.core.app.CommandRouter")
    def test_app_init_architect_mode(self, mock_router, mock_session, mock_create_ai):
        mock_ai_instance = MagicMock()
        mock_create_ai.return_value = mock_ai_instance

        app = ClioraOpsApp(Mode.ARCHITECT)

        assert app.mode == Mode.ARCHITECT
        assert app.ai is not None
        mock_create_ai.assert_called_once_with(mode=Mode.ARCHITECT)


class TestClioraOpsAppModeUpdate:
    """Test mode switching."""

    @patch("clioraOps_cli.core.app.create_ai_client")
    @patch("clioraOps_cli.core.app.SessionManager")
    @patch("clioraOps_cli.core.app.CommandRouter")
    def test_update_mode_beginner_to_architect(self, mock_router, mock_session, mock_create_ai):
        mock_create_ai.return_value = MagicMock()

        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance

        mock_router_instance = MagicMock()
        mock_router.return_value = mock_router_instance

        app = ClioraOpsApp(Mode.BEGINNER)
        assert app.mode == Mode.BEGINNER

        app.update_mode(Mode.ARCHITECT)

        assert app.mode == Mode.ARCHITECT
        mock_session_instance.update_mode.assert_called_with(Mode.ARCHITECT)
        mock_router_instance.update_mode.assert_called_with(Mode.ARCHITECT)

    @patch("clioraOps_cli.core.app.create_ai_client")
    @patch("clioraOps_cli.core.app.SessionManager")
    @patch("clioraOps_cli.core.app.CommandRouter")
    def test_update_mode_architect_to_beginner(self, mock_router, mock_session, mock_create_ai):
        mock_create_ai.return_value = MagicMock()

        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance

        mock_router_instance = MagicMock()
        mock_router.return_value = mock_router_instance

        app = ClioraOpsApp(Mode.ARCHITECT)
        assert app.mode == Mode.ARCHITECT

        app.update_mode(Mode.BEGINNER)

        assert app.mode == Mode.BEGINNER
        mock_session_instance.update_mode.assert_called_with(Mode.BEGINNER)
        mock_router_instance.update_mode.assert_called_with(Mode.BEGINNER)


class TestClioraOpsAppCommandExecution:
    """Test command execution."""

    @patch("clioraOps_cli.core.app.create_ai_client")
    @patch("clioraOps_cli.core.app.SessionManager")
    @patch("clioraOps_cli.core.app.CommandRouter")
    def test_run_single_command(self, mock_router, mock_session, mock_create_ai):
        mock_create_ai.return_value = MagicMock()

        mock_router_instance = MagicMock()
        mock_router.return_value = mock_router_instance

        app = ClioraOpsApp(Mode.BEGINNER)
        app.run("try", "docker ps")

        mock_router_instance.route.assert_called_once_with("try docker ps")

    @patch("clioraOps_cli.core.app.create_ai_client")
    @patch("clioraOps_cli.core.app.SessionManager")
    @patch("clioraOps_cli.core.app.CommandRouter")
    def test_run_command_with_multiple_args(self, mock_router, mock_session, mock_create_ai):
        mock_create_ai.return_value = MagicMock()

        mock_router_instance = MagicMock()
        mock_router.return_value = mock_router_instance

        app = ClioraOpsApp(Mode.BEGINNER)
        app.run("generate", "dockerfile", "python", "fastapi")

        mock_router_instance.route.assert_called_once_with(
            "generate dockerfile python fastapi"
        )

    @patch("clioraOps_cli.core.app.create_ai_client")
    @patch("clioraOps_cli.core.app.SessionManager")
    @patch("clioraOps_cli.core.app.CommandRouter")
    def test_run_no_args(self, mock_router, mock_session, mock_create_ai):
        mock_create_ai.return_value = MagicMock()

        mock_router_instance = MagicMock()
        mock_router.return_value = mock_router_instance

        app = ClioraOpsApp(Mode.BEGINNER)
        app.run("help")

        mock_router_instance.route.assert_called_once_with("help")


class TestClioraOpsAppComponents:
    """Test app components."""

    @patch("clioraOps_cli.core.app.create_ai_client")
    @patch("clioraOps_cli.core.app.SessionManager")
    @patch("clioraOps_cli.core.app.CommandRouter")
    def test_app_has_session_manager(self, mock_router, mock_session, mock_create_ai):
        mock_create_ai.return_value = MagicMock()
        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance

        app = ClioraOpsApp(Mode.BEGINNER)

        assert app.session is not None
        mock_session.assert_called_once()

    @patch("clioraOps_cli.core.app.create_ai_client")
    @patch("clioraOps_cli.core.app.SessionManager")
    @patch("clioraOps_cli.core.app.CommandRouter")
    def test_app_has_command_router(self, mock_router, mock_session, mock_create_ai):
        mock_create_ai.return_value = MagicMock()
        mock_router_instance = MagicMock()
        mock_router.return_value = mock_router_instance

        app = ClioraOpsApp(Mode.BEGINNER)

        assert app.command_router is not None
        mock_router.assert_called_once()


class TestClioraOpsAppModePreservation:
    """Test that mode is preserved across operations."""

    @patch("clioraOps_cli.core.app.create_ai_client")
    @patch("clioraOps_cli.core.app.SessionManager")
    @patch("clioraOps_cli.core.app.CommandRouter")
    def test_mode_preserved_after_command(self, mock_router, mock_session, mock_create_ai):
        mock_create_ai.return_value = MagicMock()

        mock_router_instance = MagicMock()
        mock_router.return_value = mock_router_instance

        app = ClioraOpsApp(Mode.ARCHITECT)
        original_mode = app.mode

        app.run("try", "ls")

        assert app.mode == original_mode

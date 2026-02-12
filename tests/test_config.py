"""
Unit tests for configuration management.
Tests config loading, saving, and mode resolution.
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
from clioraOps_cli.config.settings import load_config, save_config, resolve_mode
from clioraOps_cli.core.modes import Mode


class TestLoadConfig:
    """Test configuration loading."""
    
    @patch('clioraOps_cli.config.settings.CONFIG_FILE')
    def test_load_config_file_not_exists(self, mock_config_file):
        """Test loading config when file doesn't exist."""
        mock_config_file.exists.return_value = False
        result = load_config()
        assert result == {}
    
    @patch('clioraOps_cli.config.settings.CONFIG_FILE')
    def test_load_config_file_exists(self, mock_config_file):
        """Test loading config when file exists."""
        mock_config_file.exists.return_value = True
        mock_config_file.open = MagicMock()
        
        # Mock file content
        mock_file = MagicMock()
        mock_file.__enter__.return_value = mock_file
        mock_file.__exit__.return_value = None
        mock_file.read.return_value = '{"mode": "beginner"}'
        mock_config_file.open.return_value = mock_file
        
        # We'd need to mock json.load as well
        with patch('builtins.open', MagicMock(return_value=MagicMock(
            __enter__=MagicMock(return_value=MagicMock(read=MagicMock(return_value='{"mode": "beginner"}'))),
            __exit__=MagicMock(return_value=None)
        ))):
            with patch('json.load', return_value={"mode": "beginner"}):
                result = load_config()
                # Result should be a dict or empty dict
                assert isinstance(result, dict)
    
    @patch('clioraOps_cli.config.settings.CONFIG_FILE')
    def test_load_config_invalid_json(self, mock_config_file):
        """Test loading config with invalid JSON."""
        mock_config_file.exists.return_value = True
        with patch('builtins.open', MagicMock(side_effect=Exception("JSON error"))):
            result = load_config()
            assert result == {}


class TestSaveConfig:
    """Test configuration saving."""
    
    @patch('clioraOps_cli.config.settings.CONFIG_DIR')
    @patch('clioraOps_cli.config.settings.CONFIG_FILE')
    def test_save_config_beginner(self, mock_config_file, mock_config_dir):
        """Test saving beginner mode config."""
        mock_config_dir.mkdir = MagicMock()
        mock_file = MagicMock()
        mock_file.__enter__ = MagicMock(return_value=mock_file)
        mock_file.__exit__ = MagicMock(return_value=None)
        
        with patch('builtins.open', return_value=mock_file):
            with patch('json.dump') as mock_json_dump:
                save_config(Mode.BEGINNER)
                
                # Should call mkdir
                mock_config_dir.mkdir.assert_called_with(parents=True, exist_ok=True)
                
                # Should call json.dump
                mock_json_dump.assert_called_once()
                call_args = mock_json_dump.call_args[0]
                assert call_args[0] == {"mode": "beginner"}
    
    @patch('clioraOps_cli.config.settings.CONFIG_DIR')
    @patch('clioraOps_cli.config.settings.CONFIG_FILE')
    def test_save_config_architect(self, mock_config_file, mock_config_dir):
        """Test saving architect mode config."""
        mock_config_dir.mkdir = MagicMock()
        mock_file = MagicMock()
        mock_file.__enter__ = MagicMock(return_value=mock_file)
        mock_file.__exit__ = MagicMock(return_value=None)
        
        with patch('builtins.open', return_value=mock_file):
            with patch('json.dump') as mock_json_dump:
                save_config(Mode.ARCHITECT)
                
                mock_json_dump.assert_called_once()
                call_args = mock_json_dump.call_args[0]
                assert call_args[0] == {"mode": "architect"}


class TestResolveMode:
    """Test mode resolution logic."""
    
    def test_resolve_mode_from_cli_arg_beginner(self):
        """Test resolving mode from CLI argument (beginner)."""
        with patch('clioraOps_cli.config.settings.save_config') as mock_save:
            mode = resolve_mode("beginner")
            assert mode == Mode.BEGINNER
            mock_save.assert_called_with(Mode.BEGINNER)
    
    def test_resolve_mode_from_cli_arg_architect(self):
        """Test resolving mode from CLI argument (architect)."""
        with patch('clioraOps_cli.config.settings.save_config') as mock_save:
            mode = resolve_mode("architect")
            assert mode == Mode.ARCHITECT
            mock_save.assert_called_with(Mode.ARCHITECT)
    
    def test_resolve_mode_from_config_file(self):
        """Test resolving mode from config file."""
        with patch('clioraOps_cli.config.settings.load_config', return_value={"mode": "beginner"}):
            mode = resolve_mode(None)
            assert mode == Mode.BEGINNER
    
    def test_resolve_mode_invalid_cli_arg(self):
        """Test that invalid CLI arg raises error."""
        with pytest.raises(ValueError):
            resolve_mode("invalid_mode")
    
    def test_resolve_mode_case_insensitive(self):
        """Test that mode resolution is case insensitive."""
        with patch('clioraOps_cli.config.settings.save_config') as mock_save:
            mode = resolve_mode("BEGINNER")
            assert mode == Mode.BEGINNER
            mock_save.assert_called_with(Mode.BEGINNER)


class TestModeDefaults:
    """Test mode default values."""
    
    def test_mode_enum_has_beginner(self):
        """Test that Mode enum has BEGINNER."""
        assert hasattr(Mode, 'BEGINNER')
        assert Mode.BEGINNER is not None
    
    def test_mode_enum_has_architect(self):
        """Test that Mode enum has ARCHITECT."""
        assert hasattr(Mode, 'ARCHITECT')
        assert Mode.ARCHITECT is not None
    
    def test_mode_string_representation(self):
        """Test mode string representation."""
        assert str(Mode.BEGINNER.value) == "beginner"
        assert str(Mode.ARCHITECT.value) == "architect"

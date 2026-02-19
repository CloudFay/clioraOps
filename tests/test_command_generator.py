"""
Tests for command generator.
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from clioraOps_cli.features.command_generator import CommandGenerator, generate_shell_command
from clioraOps_cli.features.models import GeneratedCommand
from clioraOps_cli.core.modes import Mode
from clioraOps_cli.integrations.ai_provider import AIResponse, AIProviderType


class TestCommandGenerator:
    """Test suite for CommandGenerator class."""
    
    @pytest.fixture
    def mock_ai_client(self):
        """Create a mock AI client."""
        client = Mock()
        client.is_available = True
        return client
    
    def test_generator_initialization(self, mock_ai_client):
        """Test CommandGenerator initialization."""
        generator = CommandGenerator(Mode.BEGINNER, mock_ai_client)
        assert generator.mode == Mode.BEGINNER
        assert generator.ai == mock_ai_client
        assert generator.verbose is True
    
    def test_generator_beginner_mode(self, mock_ai_client):
        """Test that beginner mode sets verbose."""
        generator = CommandGenerator(Mode.BEGINNER, mock_ai_client)
        assert generator.verbose is True
    
    def test_generator_architect_mode(self, mock_ai_client):
        """Test that architect mode sets non-verbose."""
        generator = CommandGenerator(Mode.ARCHITECT, mock_ai_client)
        assert generator.verbose is False
    
    def test_generate_command_no_ai(self):
        """Test command generation fails gracefully without AI."""
        generator = CommandGenerator(Mode.BEGINNER, None)
        result = generator.generate_command("show running containers")
        assert result.success is False
        assert "AI service not available" in result.error
    
    def test_generate_command_ai_unavailable(self):
        """Test command generation fails when AI is unavailable."""
        mock_ai = Mock()
        mock_ai.is_available = False
        generator = CommandGenerator(Mode.BEGINNER, mock_ai)
        result = generator.generate_command("show running containers")
        assert result.success is False
    
    def test_generate_command_ai_error(self, mock_ai_client):
        """Test handling of AI errors."""
        mock_ai_client.chat.return_value = AIResponse(
            success=False,
            content="",
            provider=AIProviderType.GEMINI,
            error="API Error"
        )
        generator = CommandGenerator(Mode.BEGINNER, mock_ai_client)
        result = generator.generate_command("show running containers")
        assert result.success is False
        assert "Generation failed" in result.error
    
    def test_generate_command_success(self, mock_ai_client):
        """Test successful command generation."""
        response_json = {
            "success": True,
            "command": "docker ps -a",
            "explanation": "Lists all Docker containers",
            "confidence": "high",
            "warnings": []
        }
        mock_ai_client.chat.return_value = AIResponse(
            success=True,
            content=json.dumps(response_json),
            provider=AIProviderType.GEMINI
        )
        
        generator = CommandGenerator(Mode.BEGINNER, mock_ai_client)
        result = generator.generate_command("show all running containers")
        
        assert result.success is True
        assert result.command == "docker ps -a"
        assert result.explanation == "Lists all Docker containers"
        assert result.confidence == "high"
        assert result.warnings == []
    
    def test_generate_command_with_warnings(self, mock_ai_client):
        """Test command generation with safety warnings."""
        response_json = {
            "success": True,
            "command": "sudo systemctl restart nginx",
            "explanation": "Restarts the nginx service",
            "confidence": "high",
            "warnings": []
        }
        mock_ai_client.chat.return_value = AIResponse(
            success=True,
            content=json.dumps(response_json),
            provider=AIProviderType.GEMINI
        )
        
        generator = CommandGenerator(Mode.BEGINNER, mock_ai_client)
        result = generator.generate_command("restart nginx service")
        
        assert result.success is True
        assert "sudo" in result.command
        # Should have warning about sudo
        assert any("sudo" in w.lower() for w in result.warnings)
    
    def test_parse_response_invalid_json(self, mock_ai_client):
        """Test handling of invalid JSON in response."""
        mock_ai_client.chat.return_value = AIResponse(
            success=True,
            content="This is not JSON",
            provider=AIProviderType.GEMINI
        )
        
        generator = CommandGenerator(Mode.BEGINNER, mock_ai_client)
        result = generator.generate_command("show containers")
        assert result.success is False
        assert "Invalid response format" in result.error
    
    def test_parse_response_empty_command(self, mock_ai_client):
        """Test handling of empty command in response."""
        response_json = {
            "success": True,
            "command": "",
            "explanation": "No command",
            "confidence": "high",
            "warnings": []
        }
        mock_ai_client.chat.return_value = AIResponse(
            success=True,
            content=json.dumps(response_json),
            provider=AIProviderType.GEMINI
        )
        
        generator = CommandGenerator(Mode.BEGINNER, mock_ai_client)
        result = generator.generate_command("show containers")
        assert result.success is False
        assert "No command generated" in result.error
    
    def test_dangerous_pattern_rm_rf(self, mock_ai_client):
        """Test detection of dangerous rm -rf / pattern."""
        response_json = {
            "success": True,
            "command": "rm -rf /",
            "explanation": "Delete everything",
            "confidence": "high",
            "warnings": []
        }
        mock_ai_client.chat.return_value = AIResponse(
            success=True,
            content=json.dumps(response_json),
            provider=AIProviderType.GEMINI
        )
        
        generator = CommandGenerator(Mode.BEGINNER, mock_ai_client)
        result = generator.generate_command("delete everything")
        
        assert result.success is True
        assert result.command == "rm -rf /"
        assert len(result.warnings) > 0
        assert "dangerous" in result.warnings[0].lower()
    
    def test_dangerous_pattern_dd(self, mock_ai_client):
        """Test detection of dangerous dd pattern."""
        response_json = {
            "success": True,
            "command": "dd if=/dev/zero of=/dev/sda",
            "explanation": "Wipe disk",
            "confidence": "high",
            "warnings": []
        }
        mock_ai_client.chat.return_value = AIResponse(
            success=True,
            content=json.dumps(response_json),
            provider=AIProviderType.GEMINI
        )
        
        generator = CommandGenerator(Mode.BEGINNER, mock_ai_client)
        result = generator.generate_command("wipe disk")
        
        assert result.success is True
        assert len(result.warnings) > 0
        # Confidence should be lowered due to warnings
        assert result.confidence in ["medium", "low"]
    
    def test_confidence_levels(self, mock_ai_client):
        """Test handling of different confidence levels."""
        for conf_level in ["high", "medium", "low"]:
            response_json = {
                "success": True,
                "command": "ls",
                "explanation": "List files",
                "confidence": conf_level,
                "warnings": []
            }
            mock_ai_client.chat.return_value = AIResponse(
                success=True,
                content=json.dumps(response_json),
                provider=AIProviderType.GEMINI
            )
            
            generator = CommandGenerator(Mode.BEGINNER, mock_ai_client)
            result = generator.generate_command("list files")
            
            assert result.confidence == conf_level
    
    def test_invalid_confidence_normalized(self, mock_ai_client):
        """Test that invalid confidence is normalized."""
        response_json = {
            "success": True,
            "command": "ls",
            "explanation": "List files",
            "confidence": "invalid",
            "warnings": []
        }
        mock_ai_client.chat.return_value = AIResponse(
            success=True,
            content=json.dumps(response_json),
            provider=AIProviderType.GEMINI
        )
        
        generator = CommandGenerator(Mode.BEGINNER, mock_ai_client)
        result = generator.generate_command("list files")
        
        assert result.confidence == "medium"
    
    def test_ai_failure_response(self, mock_ai_client):
        """Test handling of AI failure response."""
        response_json = {
            "success": False,
            "error": "Cannot understand request"
        }
        mock_ai_client.chat.return_value = AIResponse(
            success=True,
            content=json.dumps(response_json),
            provider=AIProviderType.GEMINI
        )
        
        generator = CommandGenerator(Mode.BEGINNER, mock_ai_client)
        result = generator.generate_command("ambiguous request")
        
        assert result.success is False
        assert "Cannot understand" in result.error
    
    def test_os_context_in_prompt(self, mock_ai_client):
        """Test that OS context is included in prompt."""
        mock_ai_client.chat.return_value = AIResponse(
            success=True,
            content=json.dumps({
                "success": True,
                "command": "ls",
                "explanation": "List",
                "confidence": "high",
                "warnings": []
            }),
            provider=AIProviderType.GEMINI
        )
        
        generator = CommandGenerator(Mode.BEGINNER, mock_ai_client)
        result = generator.generate_command("list files", os_context="macos")
        
        # Check that chat was called with OS context in system prompt
        call_args = mock_ai_client.chat.call_args
        assert call_args is not None
        system_prompt = call_args[1].get('system_prompt', '')
        assert "macos" in system_prompt.lower()


class TestCommandGeneratorConvenienceFunction:
    """Test the convenience function."""
    
    @pytest.fixture
    def mock_ai(self):
        """Create mock AI client."""
        client = Mock()
        client.is_available = True
        client.chat.return_value = AIResponse(
            success=True,
            content=json.dumps({
                "success": True,
                "command": "docker ps",
                "explanation": "List containers",
                "confidence": "high",
                "warnings": []
            }),
            provider=AIProviderType.GEMINI
        )
        return client
    
    def test_convenience_function(self, mock_ai):
        """Test the generate_shell_command convenience function."""
        result = generate_shell_command("list containers", Mode.BEGINNER, mock_ai)
        
        assert result.success is True
        assert result.command == "docker ps"
    
    def test_convenience_function_default_mode(self, mock_ai):
        """Test convenience function with default mode."""
        result = generate_shell_command("list containers", ai_client=mock_ai)
        assert result.success is True


class TestSafetyChecks:
    """Test safety checking functionality."""
    
    def test_check_safety_no_warnings(self):
        """Test command with no safety issues."""
        generator = CommandGenerator(Mode.BEGINNER, None)
        warnings = generator._check_safety("ls -la")
        assert warnings == []
    
    def test_check_safety_sudo_warning(self):
        """Test sudo warning detection."""
        generator = CommandGenerator(Mode.BEGINNER, None)
        warnings = generator._check_safety("sudo systemctl restart")
        assert len(warnings) > 0
        assert any("sudo" in w.lower() for w in warnings)
    
    def test_check_safety_network_warning(self):
        """Test network command warning."""
        generator = CommandGenerator(Mode.BEGINNER, None)
        warnings = generator._check_safety("curl https://example.com")
        assert len(warnings) > 0
        assert any("network" in w.lower() for w in warnings)
    
    def test_check_safety_wget_warning(self):
        """Test wget warning."""
        generator = CommandGenerator(Mode.BEGINNER, None)
        warnings = generator._check_safety("wget https://example.com/file.tar.gz")
        assert len(warnings) > 0
    
    def test_check_safety_interactive_warning(self):
        """Test interactive command warning."""
        generator = CommandGenerator(Mode.BEGINNER, None)
        warnings = generator._check_safety("rm -i file.txt")
        assert len(warnings) > 0

"""
Tests for natural language detection.
"""

import pytest
from clioraOps_cli.core.nl_detector import NLDetector, is_natural_language


class TestNLDetector:
    """Test suite for NLDetector class."""
    
    def test_explicit_command_with_try(self):
        """Test that 'try' keyword indicates explicit command."""
        is_nl, classification = NLDetector.is_natural_language("try docker ps")
        assert is_nl is False
        assert classification == "EXPLICIT"
    
    def test_explicit_command_with_sudo(self):
        """Test that 'sudo' keyword indicates explicit command."""
        is_nl, classification = NLDetector.is_natural_language("sudo systemctl restart nginx")
        assert is_nl is False
        assert classification == "EXPLICIT"
    
    def test_explicit_with_pipe(self):
        """Test that pipes indicate explicit command."""
        is_nl, classification = NLDetector.is_natural_language("cat file.txt | grep error")
        assert is_nl is False
        assert classification == "EXPLICIT"
    
    def test_explicit_with_redirect(self):
        """Test that redirects indicate explicit command."""
        is_nl, classification = NLDetector.is_natural_language("echo test > output.txt")
        assert is_nl is False
        assert classification == "EXPLICIT"
    
    def test_explicit_with_command_chaining(self):
        """Test that command chaining indicates explicit command."""
        is_nl, classification = NLDetector.is_natural_language("npm install && npm test")
        assert is_nl is False
        assert classification == "EXPLICIT"
    
    def test_natural_language_question(self):
        """Test that questions are detected as NL."""
        is_nl, classification = NLDetector.is_natural_language("what are running containers?")
        assert is_nl is True
        assert classification == "NL"
    
    def test_natural_language_show_command(self):
        """Test that 'show' imperatives are detected as NL."""
        is_nl, classification = NLDetector.is_natural_language("show me all running containers")
        assert is_nl is True
        assert classification == "NL"
    
    def test_natural_language_find_command(self):
        """Test that 'find' requests are detected as NL."""
        is_nl, classification = NLDetector.is_natural_language("find files larger than 100MB")
        assert is_nl is True
        assert classification == "NL"
    
    def test_natural_language_list_command(self):
        """Test that 'list' imperatives are detected as NL."""
        is_nl, classification = NLDetector.is_natural_language("list all docker images")
        assert is_nl is True
        assert classification == "NL"
    
    def test_natural_language_convert_command(self):
        """Test that 'convert' requests are detected as NL."""
        is_nl, classification = NLDetector.is_natural_language("convert video.mp4 to gif")
        assert is_nl is True
        assert classification == "NL"
    
    def test_natural_language_multiple_triggers(self):
        """Test that multiple NL triggers are detected."""
        is_nl, classification = NLDetector.is_natural_language("show me files larger than 10MB in this directory")
        assert is_nl is True
        assert classification == "NL"
    
    def test_ambiguous_short_input(self):
        """Test that short ambiguous input defaults to explicit."""
        is_nl, classification = NLDetector.is_natural_language("docker ps")
        assert is_nl is False
        assert classification == "EXPLICIT"  # docker is in EXPLICIT_KEYWORDS
    
    def test_empty_input(self):
        """Test that empty input is handled."""
        is_nl, classification = NLDetector.is_natural_language("")
        assert is_nl is False
        assert classification == "EMPTY"
    
    def test_whitespace_only(self):
        """Test that whitespace-only input is handled."""
        is_nl, classification = NLDetector.is_natural_language("   ")
        assert is_nl is False
        assert classification == "EMPTY"
    
    def test_natural_language_with_preposition(self):
        """Test NL detection with prepositions."""
        is_nl, classification = NLDetector.is_natural_language("list all files in the downloads folder")
        assert is_nl is True
        assert classification == "NL"
    
    def test_natural_language_comparison(self):
        """Test NL detection with comparisons."""
        is_nl, classification = NLDetector.is_natural_language("find files larger than one gigabyte")
        assert is_nl is True
        assert classification == "NL"
    
    def test_convenience_function(self):
        """Test the convenience function."""
        assert is_natural_language("show running containers") is True
        assert is_natural_language("try docker ps") is False


class TestNLDetectorEdgeCases:
    """Test edge cases and unusual inputs."""
    
    def test_mixed_case(self):
        """Test that detection works with mixed case."""
        is_nl, _ = NLDetector.is_natural_language("SHOW ME ALL CONTAINERS")
        assert is_nl is True
    
    def test_command_with_description(self):
        """Test ambiguous input that could be both."""
        # "get status" with get trigger but short input
        is_nl, _ = NLDetector.is_natural_language("get status")
        # Short input defaults to explicit
        assert is_nl is False
    
    def test_tool_names_as_start_word(self):
        """Test that tool names at start are treated as explicit."""
        is_nl, classification = NLDetector.is_natural_language("git status")
        assert is_nl is False
        assert classification == "EXPLICIT"
    
    def test_npm_command(self):
        """Test npm command detection."""
        is_nl, classification = NLDetector.is_natural_language("npm install")
        assert is_nl is False
        assert classification == "EXPLICIT"
    
    def test_python_command(self):
        """Test python command detection."""
        is_nl, classification = NLDetector.is_natural_language("python script.py")
        assert is_nl is False
        assert classification == "EXPLICIT"
    
    def test_help_me_pattern(self):
        """Test 'help me' pattern."""
        is_nl, _ = NLDetector.is_natural_language("help me analyze this error")
        assert is_nl is True
    
    def test_can_you_pattern(self):
        """Test 'can you' pattern."""
        is_nl, _ = NLDetector.is_natural_language("can you explain docker")
        assert is_nl is True
    
    def test_please_pattern(self):
        """Test 'please' pattern."""
        is_nl, _ = NLDetector.is_natural_language("please show running processes")
        assert is_nl is True


class TestImperativeDetection:
    """Test imperative form detection."""
    
    def test_show_imperative(self):
        """Test 'show' imperative."""
        assert NLDetector._is_imperative("show running containers") is True
    
    def test_list_imperative(self):
        """Test 'list' imperative."""
        assert NLDetector._is_imperative("list all files") is True
    
    def test_find_imperative(self):
        """Test 'find' imperative."""
        assert NLDetector._is_imperative("find large files") is True
    
    def test_non_imperative(self):
        """Test non-imperative."""
        assert NLDetector._is_imperative("docker ps") is False


class TestNLStructure:
    """Test natural language structure detection."""
    
    def test_long_input_is_nl(self):
        """Test that longer inputs are marked as NL."""
        text = "show me all running docker containers with their resource usage"
        assert NLDetector._has_nl_structure(text) is True
    
    def test_short_input_not_nl(self):
        """Test that short inputs aren't marked as NL by structure alone."""
        text = "show me"
        assert NLDetector._has_nl_structure(text) is False
    
    def test_preposition_pattern(self):
        """Test preposition patterns."""
        text = "files in the downloads folder"
        assert NLDetector._has_nl_structure(text) is True
    
    def test_comparison_pattern(self):
        """Test comparison patterns."""
        text = "find files larger than 100MB"
        assert NLDetector._has_nl_structure(text) is True

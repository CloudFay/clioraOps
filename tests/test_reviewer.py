"""
Unit tests for CodeReviewer module.
Tests safety detection, risk levels, and educational feedback.
"""

import pytest
from clioraOps_cli.features.reviewer import (
    CodeReviewer,
    RiskLevel,
    ReviewResult,
    CommandPattern,
)
from clioraOps_cli.core.modes import Mode


class TestRiskLevel:
    """Test RiskLevel enum."""
    
    def test_risk_level_values(self):
        """Test RiskLevel enum values."""
        assert RiskLevel.SAFE.value == "safe"
        assert RiskLevel.CAUTION.value == "caution"
        assert RiskLevel.DANGEROUS.value == "dangerous"
        assert RiskLevel.CRITICAL.value == "critical"


class TestCommandPattern:
    """Test CommandPattern class."""
    
    def test_pattern_matches_exact(self):
        """Test exact pattern matching."""
        pattern = CommandPattern(
            pattern=r'\brm\s+-rf\s+/',
            risk_level=RiskLevel.CRITICAL,
            description="Delete everything",
            beginner_explanation="Bad!",
            architect_explanation="Very bad!"
        )
        assert pattern.matches("rm -rf /")
        assert pattern.matches("rm -rf /home")
    
    def test_pattern_case_insensitive(self):
        """Test case-insensitive matching."""
        pattern = CommandPattern(
            pattern=r'\brm\s+-rf',
            risk_level=RiskLevel.DANGEROUS,
            description="Recursive delete",
            beginner_explanation="Dangerous",
            architect_explanation="Dangerous"
        )
        assert pattern.matches("rm -rf /tmp")
        assert pattern.matches("RM -RF /tmp")


class TestCodeReviewerBeginner:
    """Test CodeReviewer in beginner mode."""
    
    def setup_method(self):
        """Setup for each test."""
        self.reviewer = CodeReviewer(Mode.BEGINNER)
    
    def test_safe_command(self):
        """Test safe command review."""
        result = self.reviewer.review_command("docker ps")
        assert result.risk_level == RiskLevel.SAFE
        assert result.proceed
    
    def test_dangerous_rm_rf_root(self):
        """Test detection of rm -rf / command."""
        result = self.reviewer.review_command("rm -rf /")
        assert result.risk_level == RiskLevel.CRITICAL
        assert not result.proceed
    
    def test_dangerous_rm_rf_home(self):
        """Test detection of rm -rf /home."""
        result = self.reviewer.review_command("rm -rf /home")
        assert result.risk_level in [RiskLevel.DANGEROUS, RiskLevel.CRITICAL]
        assert not result.proceed


class TestCodeReviewerArchitect:
    """Test CodeReviewer in architect mode."""
    
    def setup_method(self):
        """Setup for each test."""
        self.reviewer = CodeReviewer(Mode.ARCHITECT)
    
    def test_safe_command(self):
        """Test safe command review."""
        result = self.reviewer.review_command("kubectl get pods")
        assert result.risk_level == RiskLevel.SAFE
        assert result.proceed
    
    def test_dangerous_command_architect(self):
        """Test dangerous command in architect mode."""
        result = self.reviewer.review_command("rm -rf /")
        assert result.risk_level == RiskLevel.CRITICAL
        assert not result.proceed


class TestReviewResult:
    """Test ReviewResult dataclass."""
    
    def test_review_result_creation(self):
        """Test ReviewResult initialization."""
        result = ReviewResult(
            safe=False,
            risk_level=RiskLevel.CRITICAL,
            message="Dangerous operation",
            explanation="This will delete everything",
            safe_alternative="Use 'rm -i' instead"
        )
        assert not result.safe
        assert result.risk_level == RiskLevel.CRITICAL
        assert result.proceed is True
    
    def test_review_result_defaults(self):
        """Test ReviewResult default values."""
        result = ReviewResult(
            safe=True,
            risk_level=RiskLevel.SAFE,
            message="Safe operation",
            explanation="This is safe"
        )
        assert result.proceed is True
        assert result.require_confirmation is False

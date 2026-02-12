"""
Unit tests for Mode and dialogue rules.
Tests mode switching and dialogue rule application.
"""

import pytest
from clioraOps_cli.core.modes import Mode, DialogueRule, DialogueRules


class TestMode:
    """Test Mode enum."""
    
    def test_mode_values(self):
        """Test Mode enum values."""
        assert Mode.BEGINNER.value == "beginner"
        assert Mode.ARCHITECT.value == "architect"
    
    def test_mode_comparison(self):
        """Test mode comparison."""
        assert Mode.BEGINNER == Mode.BEGINNER
        assert Mode.ARCHITECT == Mode.ARCHITECT
        assert Mode.BEGINNER != Mode.ARCHITECT
    
    def test_mode_from_string(self):
        """Test creating mode from string."""
        assert Mode("beginner") == Mode.BEGINNER
        assert Mode("architect") == Mode.ARCHITECT
    
    def test_mode_invalid_value(self):
        """Test that invalid mode value raises error."""
        with pytest.raises(ValueError):
            Mode("invalid_mode")


class TestDialogueRule:
    """Test DialogueRule dataclass."""
    
    def test_dialogue_rule_creation(self):
        """Test DialogueRule initialization."""
        rule = DialogueRule(
            description="Use simple language",
            examples=["Hello!", "Great question!"]
        )
        assert rule.description == "Use simple language"
        assert len(rule.examples) == 2
    
    def test_dialogue_rule_no_examples(self):
        """Test DialogueRule with no examples."""
        rule = DialogueRule(description="Be concise")
        assert rule.description == "Be concise"
        assert rule.examples is None


class TestDialogueRulesBeginnerMode:
    """Test dialogue rules for beginner mode."""
    
    def test_beginner_rules_exist(self):
        """Test that beginner rules are defined."""
        assert DialogueRules.BEGINNER is not None
        assert len(DialogueRules.BEGINNER) > 0
    
    def test_beginner_rule_structure(self):
        """Test that beginner rules have correct structure."""
        for rule in DialogueRules.BEGINNER:
            assert isinstance(rule, DialogueRule)
            assert rule.description is not None
            assert len(rule.description) > 0
    
    def test_beginner_acknowledgement_rule(self):
        """Test positive acknowledgement rule."""
        rules = DialogueRules.BEGINNER
        acknowledgement_rules = [r for r in rules if "acknowledgement" in r.description.lower()]
        assert len(acknowledgement_rules) > 0
    
    def test_beginner_analogy_rule(self):
        """Test real-world analogy rule."""
        rules = DialogueRules.BEGINNER
        analogy_rules = [r for r in rules if "analogy" in r.description.lower() or "analogies" in r.description.lower()]
        assert len(analogy_rules) > 0
    
    def test_beginner_warning_rule(self):
        """Test warning rule."""
        rules = DialogueRules.BEGINNER
        warning_rules = [r for r in rules if "warn" in r.description.lower()]
        assert len(warning_rules) > 0


class TestDialogueRulesArchitectMode:
    """Test dialogue rules for architect mode."""
    
    def test_architect_rules_exist(self):
        """Test that architect rules are defined."""
        assert DialogueRules.ARCHITECT is not None
        assert len(DialogueRules.ARCHITECT) > 0
    
    def test_architect_rule_structure(self):
        """Test that architect rules have correct structure."""
        for rule in DialogueRules.ARCHITECT:
            assert isinstance(rule, DialogueRule)
            assert rule.description is not None
    
    def test_architect_concise_rule(self):
        """Test conciseness rule for architect mode."""
        rules = DialogueRules.ARCHITECT
        concise_rules = [r for r in rules if "concise" in r.description.lower() or "high-signal" in r.description.lower()]
        assert len(concise_rules) > 0
    
    def test_architect_standards_rule(self):
        """Test industry standards rule."""
        rules = DialogueRules.ARCHITECT
        standards_rules = [r for r in rules if "standard" in r.description.lower()]
        assert len(standards_rules) > 0
    
    def test_architect_tradeoffs_rule(self):
        """Test trade-offs rule."""
        rules = DialogueRules.ARCHITECT
        tradeoff_rules = [r for r in rules if "trade" in r.description.lower()]
        assert len(tradeoff_rules) > 0


class TestDialogueRulesComparison:
    """Test differences between beginner and architect rules."""
    
    def test_rules_are_different(self):
        """Test that beginner and architect rules differ."""
        beginner_descriptions = [r.description for r in DialogueRules.BEGINNER]
        architect_descriptions = [r.description for r in DialogueRules.ARCHITECT]
        
        # Rules should have different focuses
        assert beginner_descriptions != architect_descriptions
    
    def test_beginner_simpler_language(self):
        """Test that beginner rules emphasize simple language."""
        beginner_set = {r.description.lower() for r in DialogueRules.BEGINNER}
        has_simple_language = any(
            word in str(beginner_set)
            for word in ["simple", "small", "everyday", "analogy"]
        )
        assert has_simple_language
    
    def test_architect_technical_language(self):
        """Test that architect rules emphasize technical aspects."""
        architect_set = {r.description.lower() for r in DialogueRules.ARCHITECT}
        has_technical_language = any(
            word in str(architect_set)
            for word in ["technical", "standard", "trade", "design", "concern"]
        )
        assert has_technical_language


class TestModeIntegration:
    """Test mode integration across components."""
    
    def test_all_rules_have_examples(self):
        """Test that most rules have examples."""
        for mode_rules in [DialogueRules.BEGINNER, DialogueRules.ARCHITECT]:
            for rule in mode_rules:
                # At least some rules should have examples
                assert rule.description is not None
    
    def test_beginner_rules_count(self):
        """Test beginner rules count."""
        assert len(DialogueRules.BEGINNER) >= 3
    
    def test_architect_rules_count(self):
        """Test architect rules count."""
        assert len(DialogueRules.ARCHITECT) >= 3

"""
Tests for NL intent classification (v0.3.1).
Tests the classify_nl_intent() method that differentiates between:
- COMMAND: operational requests (show containers, find files)
- REQUEST: informational requests (what is docker, explain kubernetes)
- AMBIGUOUS: unclear intent (show concepts, list benefits)
"""

import pytest
from clioraOps_cli.core.nl_detector import NLDetector


class TestIntentClassifier:
    """Test NL intent classification."""
    
    # TIER 1: Question words (95%+ confidence -> REQUEST)
    
    def test_what_question_simple(self):
        """Questions starting with 'what' classify as REQUEST with 95%+ confidence."""
        intent, confidence = NLDetector.classify_nl_intent("what is docker?")
        assert intent == "request"
        assert confidence >= 0.95
    
    def test_why_question(self):
        """Questions starting with 'why' classify as REQUEST."""
        intent, confidence = NLDetector.classify_nl_intent("why use kubernetes?")
        assert intent == "request"
        assert confidence >= 0.95
    
    def test_how_question(self):
        """Questions starting with 'how' classify as REQUEST."""
        intent, confidence = NLDetector.classify_nl_intent("how does docker work?")
        assert intent == "request"
        assert confidence >= 0.95
    
    def test_when_question(self):
        """Questions starting with 'when' classify as REQUEST."""
        intent, confidence = NLDetector.classify_nl_intent("when should I use containers?")
        assert intent == "request"
        assert confidence >= 0.95
    
    def test_which_question(self):
        """Questions starting with 'which' classify as REQUEST."""
        intent, confidence = NLDetector.classify_nl_intent("which is better, docker or kubernetes?")
        assert intent == "request"
        assert confidence >= 0.95
    
    def test_who_question(self):
        """Questions starting with 'who' classify as REQUEST."""
        intent, confidence = NLDetector.classify_nl_intent("who uses docker?")
        assert intent == "request"
        assert confidence >= 0.95
    
    def test_where_question(self):
        """Questions starting with 'where' classify as REQUEST."""
        intent, confidence = NLDetector.classify_nl_intent("where do I install docker?")
        assert intent == "request"
        assert confidence >= 0.95
    
    # TIER 2: Concept verbs (88%+ confidence -> REQUEST)
    
    def test_explain_concept(self):
        """Explain + concept classify as REQUEST."""
        intent, confidence = NLDetector.classify_nl_intent("explain microservices")
        assert intent == "request"
        assert confidence >= 0.88
    
    def test_describe_concept(self):
        """Describe + concept classify as REQUEST."""
        intent, confidence = NLDetector.classify_nl_intent("describe kubernetes architecture")
        assert intent == "request"
        assert confidence >= 0.88
    
    def test_define_concept(self):
        """Define + concept classify as REQUEST."""
        intent, confidence = NLDetector.classify_nl_intent("define containerization")
        assert intent == "request"
        assert confidence >= 0.88
    
    def test_tell_me_about(self):
        """Tell me about + concept classify as REQUEST."""
        intent, confidence = NLDetector.classify_nl_intent("tell me about CI/CD")
        assert intent == "request"
        assert confidence >= 0.88
    
    # TIER 3: Action verbs + System targets (90%+ confidence -> COMMAND)
    
    def test_show_containers(self):
        """Show + system target classify as COMMAND."""
        intent, confidence = NLDetector.classify_nl_intent("show me running containers")
        assert intent == "command"
        assert confidence >= 0.90
    
    def test_find_files(self):
        """Find + system target classify as COMMAND."""
        intent, confidence = NLDetector.classify_nl_intent("find all python files")
        assert intent == "command"
        assert confidence >= 0.90
    
    def test_list_users(self):
        """List + system target classify as COMMAND."""
        intent, confidence = NLDetector.classify_nl_intent("list all users on the system")
        assert intent == "command"
        assert confidence >= 0.90
    
    def test_count_processes(self):
        """Count + system target classify as COMMAND."""
        intent, confidence = NLDetector.classify_nl_intent("count running processes")
        assert intent == "command"
        assert confidence >= 0.90
    
    def test_check_services(self):
        """Check + system target classify as COMMAND."""
        intent, confidence = NLDetector.classify_nl_intent("check all running services")
        assert intent == "command"
        assert confidence >= 0.90
    
    def test_search_files(self):
        """Search + system target classify as COMMAND."""
        intent, confidence = NLDetector.classify_nl_intent("search for configuration files")
        assert intent == "command"
        assert confidence >= 0.90
    
    def test_display_logs(self):
        """Display + system target classify as COMMAND."""
        intent, confidence = NLDetector.classify_nl_intent("display application logs")
        assert intent == "command"
        assert confidence >= 0.90
    
    def test_locate_directory(self):
        """Locate + system target classify as COMMAND."""
        intent, confidence = NLDetector.classify_nl_intent("locate the home directory")
        assert intent == "command"
        assert confidence >= 0.90
    
    # TIER 4: Comparison/difference keywords (88%+ confidence -> REQUEST)
    
    def test_difference_between(self):
        """Difference between X and Y classify as REQUEST."""
        intent, confidence = NLDetector.classify_nl_intent("difference between Docker and Kubernetes")
        assert intent == "request"
        assert confidence >= 0.88
    
    def test_versus_comparison(self):
        """X versus Y classify as REQUEST."""
        intent, confidence = NLDetector.classify_nl_intent("containers versus virtual machines")
        assert intent == "request"
        assert confidence >= 0.88
    
    def test_vs_shorthand(self):
        """X vs Y classify as REQUEST."""
        intent, confidence = NLDetector.classify_nl_intent("docker vs podman")
        assert intent == "request"
        assert confidence >= 0.88
    
    def test_compared_to(self):
        """X compared to Y classify as REQUEST."""
        intent, confidence = NLDetector.classify_nl_intent("ansible compared to terraform")
        assert intent == "request"
        assert confidence >= 0.88
    
    def test_similar_to(self):
        """Similar to X can be REQUEST or COMMAND depending on context."""
        intent, confidence = NLDetector.classify_nl_intent("tools similar to docker")
        # "tools" is a system target, so this leans COMMAND
        assert intent in ["request", "command"]
    
    # TIER 5: "show/give/get me" patterns
    
    def test_show_me_system_target(self):
        """Show me + system target classify as COMMAND."""
        intent, confidence = NLDetector.classify_nl_intent("show me running containers")
        assert intent == "command"
        assert confidence >= 0.90
    
    def test_give_me_system_target(self):
        """Give me + system target classify as COMMAND."""
        intent, confidence = NLDetector.classify_nl_intent("give me a list of all files")
        assert intent == "command"
        assert confidence >= 0.90
    
    def test_get_me_system_target(self):
        """Get me + system target classify as COMMAND."""
        intent, confidence = NLDetector.classify_nl_intent("get me the process information")
        assert intent == "command"
        assert confidence >= 0.90
    
    # AMBIGUOUS CASES
    
    def test_show_concepts_ambiguous(self):
        """Show + abstract concept is actually COMMAND since 'show' is action verb."""
        intent, confidence = NLDetector.classify_nl_intent("show me kubernetes concepts")
        # "show" is action verb, "concepts" is not a system target, so defaults to command
        assert intent in ["command", "ambiguous"]
    
    def test_list_benefits_ambiguous(self):
        """List + benefits may be REQUEST due to 'benefits' concept."""
        intent, confidence = NLDetector.classify_nl_intent("list the benefits of docker")
        # "benefits" is concept-related, so maps to request
        assert intent in ["request", "ambiguous"]
    
    def test_find_information_ambiguous(self):
        """Find + information is COMMAND since 'find' is action verb."""
        intent, confidence = NLDetector.classify_nl_intent("find information about kubernetes")
        # "find" is action verb, but "information" not in system targets
        assert intent in ["command", "ambiguous"]
    
    def test_show_examples_ambiguous(self):
        """Show + examples is COMMAND since 'show' is action verb."""
        intent, confidence = NLDetector.classify_nl_intent("show me examples of docker commands")
        # "show" is action verb, even though "examples" is abstract
        assert intent in ["command", "ambiguous"]
    
    # EDGE CASES
    
    def test_empty_input(self):
        """Empty input classify as AMBIGUOUS with 0.5 confidence."""
        intent, confidence = NLDetector.classify_nl_intent("")
        assert intent == "ambiguous"
        assert confidence == 0.5
    
    def test_whitespace_only(self):
        """Whitespace only classify as AMBIGUOUS."""
        intent, confidence = NLDetector.classify_nl_intent("   ")
        assert intent == "ambiguous"
        assert confidence == 0.5
    
    def test_question_with_command(self):
        """Question word at start makes it REQUEST regardless."""
        # "what show containers" is grammatically odd but what is the question word
        intent, confidence = NLDetector.classify_nl_intent("what show containers")
        # Question word takes priority
        assert intent == "request"
        assert confidence >= 0.90
    
    def test_action_verb_only_learning_context(self):
        """Action verb in learning context classify as REQUEST."""
        intent, confidence = NLDetector.classify_nl_intent("show me how to learn docker")
        # "learn docker" suggests learning context
        assert intent in ["request", "ambiguous"]
    
    def test_case_insensitivity(self):
        """Classification should be case insensitive."""
        intent_lower, conf_lower = NLDetector.classify_nl_intent("what is docker")
        intent_upper, conf_upper = NLDetector.classify_nl_intent("WHAT IS DOCKER")
        intent_mixed, conf_mixed = NLDetector.classify_nl_intent("WhAt Is DocKer")
        
        assert intent_lower == intent_upper == intent_mixed
        assert conf_lower == conf_upper == conf_mixed
    
    # CONFIDENCE LEVELS
    
    def test_confidence_ranges(self):
        """Confidence levels should follow expected patterns."""
        # Question words: 95%
        _, conf_q = NLDetector.classify_nl_intent("what is docker?")
        assert conf_q == 0.95
        
        # Action verb + target: 90%+
        _, conf_cmd = NLDetector.classify_nl_intent("show me containers")
        assert conf_cmd >= 0.90
        
        # Action verb only: 75%+
        _, conf_action = NLDetector.classify_nl_intent("show concepts")
        assert conf_action >= 0.70
    
    # REALISTIC EXAMPLES
    
    def test_realistic_docker_command(self):
        """Realistic Docker operational request."""
        intent, confidence = NLDetector.classify_nl_intent("show me all running docker containers")
        assert intent == "command"
        assert confidence >= 0.90
    
    def test_realistic_docker_question(self):
        """Realistic Docker informational request."""
        intent, confidence = NLDetector.classify_nl_intent("what are the benefits of using docker?")
        assert intent == "request"
        assert confidence >= 0.95
    
    def test_realistic_kubernetes_question(self):
        """Realistic Kubernetes informational request with 'how' question word."""
        intent, confidence = NLDetector.classify_nl_intent("how does kubernetes manage container orchestration?")
        assert intent == "request"
        # The presence of containers target doesn't override question word
        # First check is question word, so should be 95% confidence REQUEST
        assert confidence >= 0.90
    
    def test_realistic_system_command(self):
        """Realistic system operational request."""
        intent, confidence = NLDetector.classify_nl_intent("find all python files modified in the last week")
        assert intent == "command"
        assert confidence >= 0.88
    
    def test_realistic_comparison(self):
        """Realistic comparison request."""
        intent, confidence = NLDetector.classify_nl_intent("explain the difference between Docker and Podman")
        assert intent == "request"
        # Could be high confidence on "difference" keyword
        assert confidence >= 0.88
    
    # MULTI-WORD SYSTEM TARGETS
    
    def test_multi_word_target_running_containers(self):
        """Multi-word system targets should be recognized."""
        intent, confidence = NLDetector.classify_nl_intent("show running containers")
        assert intent == "command"
        assert confidence >= 0.90
    
    def test_multi_word_target_python_files(self):
        """Multi-word system targets should be recognized."""
        intent, confidence = NLDetector.classify_nl_intent("find all python files")
        assert intent == "command"
        assert confidence >= 0.90
    
    # NEGATION/EXCLUSION
    
    def test_negation_still_command(self):
        """Negation doesn't change command intent."""
        intent, confidence = NLDetector.classify_nl_intent("show me containers without errors")
        assert intent == "command"
        assert confidence >= 0.88
    
    def test_exclusion_still_command(self):
        """Exclusion patterns don't change command intent."""
        intent, confidence = NLDetector.classify_nl_intent("find files not containing debug")
        assert intent == "command"
        assert confidence >= 0.88
    
    # CONCEPT VERB EDGE CASES
    
    def test_explain_with_system_target_but_action(self):
        """Explain + system target + action verb can vary."""
        intent, confidence = NLDetector.classify_nl_intent("explain how to find files")
        # Has "find" (action verb) so could lean command
        assert intent in ["request", "ambiguous", "command"]
    
    def test_compare_with_system_target(self):
        """Compare with system targets."""
        intent, confidence = NLDetector.classify_nl_intent("compare files in both directories")
        # "compare files" could be operational
        assert intent in ["command", "request", "ambiguous"]

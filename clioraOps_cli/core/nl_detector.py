"""
Natural Language detection for ClioraOps commands.
Distinguishes between natural language requests and explicit commands.
"""

import re
from typing import Tuple


class NLDetector:
    """Detects and classifies user input as natural language or explicit command."""
    
    # Explicit command keywords that indicate a structured command
    EXPLICIT_KEYWORDS = {'try', 'run', 'execute', 'sudo', 'docker', 'git', 'python', 'pip', 'npm', 'yarn'}
    
    # NL trigger words that suggest natural language intent
    NL_TRIGGERS = {
        'show', 'list', 'find', 'search', 'display', 'print', 'what', 'how', 'why',
        'tell', 'convert', 'translate', 'generate', 'create', 'build', 'make',
        'check', 'verify', 'compare', 'analyze', 'count', 'sum', 'sort',
        'help', 'explain', 'summarize', 'describe', 'list all', 'give me',
        'can you', 'could you', 'please', 'get me', 'show me', 'do you'
    }
    
    # Patterns that indicate explicit command syntax
    EXPLICIT_PATTERNS = [
        r'^try\s+',                    # starts with 'try'
        r'^\s*\$',                     # starts with shell prompt $
        r'^[a-z]+\s+[-]',              # command with flags (e.g., 'docker -ps')
        r'[|>]',                        # contains pipes or redirects
        r'&&|\|\||;',                  # contains command chaining
    ]
    
    # Question words indicating informational requests
    QUESTION_WORDS = {'what', 'why', 'how', 'when', 'which', 'who', 'where', 'what\'s', "what's"}
    
    # Action verbs indicating operational commands
    ACTION_VERBS = {
        'show', 'find', 'list', 'count', 'check', 'get', 'search', 'display', 'locate',
        'run', 'execute', 'do', 'perform', 'make', 'create', 'build', 'fetch', 'retrieve'
    }
    
    # System targets/objects (things users operate on)
    SYSTEM_TARGETS = {
        'container', 'containers', 'image', 'images', 'service', 'services',
        'file', 'files', 'directory', 'folder', 'process', 'processes',
        'port', 'ports', 'user', 'users', 'group', 'groups', 'package', 'packages',
        'network', 'networks', 'volume', 'volumes', 'database', 'databases',
        'log', 'logs', 'config', 'configuration', 'resource', 'resources'
    }
    
    # Concept verbs indicating informational requests (not operational)
    CONCEPT_VERBS = {
        'explain', 'describe', 'define', 'understand', 'tell', 'teach',
        'compare', 'difference', 'versus', 'vs', 'benefit', 'advantage'
    }
    
    @classmethod
    def is_natural_language(cls, user_input: str) -> Tuple[bool, str]:
        """
        Determine if user input is natural language or explicit command.
        
        Args:
            user_input: User's input string
            
        Returns:
            Tuple of (is_nl: bool, classification: str)
            - is_nl: True if input is natural language
            - classification: Reason for classification ("NL", "EXPLICIT", "AMBIGUOUS")
        """
        user_input = user_input.strip()
        
        if not user_input:
            return False, "EMPTY"
        
        # Check for explicit command patterns first (high confidence)
        for pattern in cls.EXPLICIT_PATTERNS:
            if re.search(pattern, user_input):
                return False, "EXPLICIT"
        
        # Check if starts with explicit keyword
        first_word = user_input.split()[0].lower()
        if first_word in cls.EXPLICIT_KEYWORDS:
            return False, "EXPLICIT"
        
        # Check for natural language triggers
        lower_input = user_input.lower()
        trigger_count = sum(1 for trigger in cls.NL_TRIGGERS if trigger in lower_input)
        
        # If multiple NL triggers found, likely NL
        if trigger_count >= 2:
            return True, "NL"
        
        # If at least one NL trigger and input is a question or imperative
        if trigger_count >= 1:
            if '?' in user_input or cls._is_imperative(user_input):
                return True, "NL"
        
        # Check for very short input (likely explicit)
        if len(user_input.split()) <= 2:
            return False, "EXPLICIT"
        
        # If input contains typical NL structure (longer, natural phrasing)
        if cls._has_nl_structure(user_input):
            return True, "NL"
        
        # Default to explicit for ambiguous cases
        return False, "AMBIGUOUS"
    
    @staticmethod
    def _is_imperative(text: str) -> bool:
        """Check if text appears to be an imperative command."""
        # Common imperative verbs at start
        imperatives = {
            'show', 'list', 'find', 'search', 'display', 'print',
            'get', 'fetch', 'retrieve', 'convert', 'generate',
            'create', 'build', 'check', 'verify', 'analyze'
        }
        first_word = text.split()[0].lower()
        return first_word in imperatives
    
    @classmethod
    def classify_nl_intent(cls, user_input: str) -> Tuple[str, float]:
        """
        Classify the intent of a natural language input.
        
        Distinguishes between:
        - "command": Operational request (show containers, find files)
        - "request": Informational request (what is docker, explain kubernetes)
        - "ambiguous": Unclear intent (show concepts, list benefits)
        
        Args:
            user_input: Natural language user input
            
        Returns:
            Tuple of (intent: str, confidence: float)
            - intent: "command", "request", or "ambiguous"
            - confidence: Float between 0.0 and 1.0 (higher = more certain)
        """
        user_input = user_input.strip().lower()
        
        if not user_input:
            return "ambiguous", 0.5
        
        # TIER 1: Question words (95%+ confidence -> REQUEST)
        # Check this FIRST - question words override everything
        first_word = user_input.split()[0]
        if first_word in cls.QUESTION_WORDS:
            return "request", 0.95
        
        # TIER 2: Concept verbs (88%+ confidence -> REQUEST)
        if any(verb in user_input for verb in cls.CONCEPT_VERBS):
            # But check if it's actually action-based (e.g., "compare files")
            if any(target in user_input for target in cls.SYSTEM_TARGETS):
                if any(action in user_input for action in {'find', 'list', 'show', 'count'}):
                    return "command", 0.75  # e.g., "compare files"
            return "request", 0.88
        
        # TIER 3: Action verbs + System targets (90%+ confidence -> COMMAND)
        has_action_verb = any(verb in user_input for verb in cls.ACTION_VERBS)
        has_system_target = any(target in user_input for target in cls.SYSTEM_TARGETS)
        
        if has_action_verb and has_system_target:
            return "command", 0.90
        
        if has_action_verb:
            # Just action verb without clear target
            # Check if it's a learning context
            if any(word in user_input for word in {'learn', 'understand', 'know', 'help me'}):
                return "request", 0.70
            return "command", 0.75
        
        # TIER 4: Comparison/difference keywords (88%+ confidence -> REQUEST)
        if any(word in user_input for word in {'difference', 'versus', 'vs', 'compared', 'similar'}):
            return "request", 0.88
        
        # TIER 5: "show/list me" patterns
        if re.search(r'(show|give|get)\s+me\s+', user_input):
            if any(target in user_input for target in cls.SYSTEM_TARGETS):
                return "command", 0.92
            # "show me concepts" - ambiguous
            if any(word in user_input for word in {'concept', 'idea', 'example', 'benefit', 'advantage'}):
                return "ambiguous", 0.60
            return "command", 0.80
        
        # Default: Ambiguous
        return "ambiguous", 0.50

    @staticmethod
    def _has_nl_structure(text: str) -> bool:
        """Check if text has natural language structure."""
        word_count = len(text.split())
        # Longer inputs are more likely to be NL
        if word_count >= 4:
            return True
        
        # Check for natural phrasing patterns
        nl_patterns = [
            r'all\s+\w+',                 # "all files"
            r'(?:larger|smaller|bigger|newer)\s+than',  # comparisons
            r'(?:in|from|to|for)\s+\w+',  # prepositions
            r'\b(?:with|without|using)\b', # with/without
        ]
        
        for pattern in nl_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False


def is_natural_language(user_input: str) -> bool:
    """
    Convenience function to check if input is natural language.
    
    Args:
        user_input: User's input string
        
    Returns:
        True if input should be treated as natural language, False for explicit command
    """
    is_nl, _ = NLDetector.is_natural_language(user_input)
    return is_nl

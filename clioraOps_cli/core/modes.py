"""
Mode definitions and dialogue rules for ClioraOps.
"""

from enum import Enum
from dataclasses import dataclass
from typing import List


class Mode(Enum):
    """Communication modes for ClioraOps."""
    BEGINNER = "beginner"
    ARCHITECT = "architect"


@dataclass
class DialogueRule:
    """A single dialogue rule with examples."""
    description: str
    examples: List[str] = None


class DialogueRules:
    """Dialogue rules for each mode."""
    
    BEGINNER = [
        DialogueRule(
            "Start with a positive acknowledgement",
            ["Great question!", "I love that you're exploring this!"]
        ),
        DialogueRule(
            "Use concrete real-world analogies",
            ["Like a traffic light", "Think of it as a librarian"]
        ),
        DialogueRule(
            "Break complex tasks into small, safe steps",
            ["First, let's...", "Then we'll..."]
        ),
        DialogueRule(
            "Explicitly warn about potential risks",
            ["⚠️ This could...", "Be careful, this affects..."]
        ),
        DialogueRule(
            "End with a check-in question",
            ["Does that make sense?", "Shall we try it?", "Ready to proceed?"]
        ),
    ]
    
    ARCHITECT = [
        DialogueRule(
            "Be concise and high-signal",
            ["Focus: CAP theorem", "Key metric: P99 latency"]
        ),
        DialogueRule(
            "Reference industry standards",
            ["Per NIST guidelines...", "12-Factor App principle 3..."]
        ),
        DialogueRule(
            "Focus on system design pillars",
            ["Reliability concern:", "Scalability bottleneck:"]
        ),
        DialogueRule(
            "Critique standard approaches",
            ["Edge case: network partition", "Failure mode: cascade"]
        ),
        DialogueRule(
            "Offer trade-offs",
            ["Best Practice vs Pragmatic:", "Cost vs Performance:"]
        ),
    ]
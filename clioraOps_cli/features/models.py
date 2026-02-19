from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, List

class DiagramFormat(Enum):
    """Output format for diagrams."""
    ASCII = "ascii"
    PNG = "png"
    SVG = "svg"
    MERMAID = "mermaid"

class ArchitecturePattern(Enum):
    """Common architecture patterns."""
    MICROSERVICES = "microservices"
    MONOLITH = "monolith"
    SERVERLESS = "serverless"
    EVENT_DRIVEN = "event_driven"
    LAYERED = "layered"
    CICD_PIPELINE = "cicd_pipeline"
    KUBERNETES = "kubernetes"
    THREE_TIER = "three_tier"
    LAMBDA = "lambda_architecture"

@dataclass
class DiagramResult:
    """Result of diagram generation."""
    success: bool
    format: DiagramFormat
    filepath: Optional[str] = None
    ascii_output: Optional[str] = None
    error: Optional[str] = None
    explanation: str = ""


@dataclass
class GeneratedCommand:
    """Result of natural language to command translation."""
    success: bool
    command: str = ""
    explanation: str = ""
    confidence: str = "medium"  # "high", "medium", "low"
    warnings: List[str] = field(default_factory=list)
    error: Optional[str] = None

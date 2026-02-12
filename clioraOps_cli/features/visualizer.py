"""
ArchitectureVisualizer Module for ClioraOps

Generates visual architecture diagrams in multiple formats:
- ASCII art for quick CLI viewing
- PNG/SVG diagrams using diagrams library
- Mermaid diagrams for documentation

Provides educational explanations for each architecture pattern.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import subprocess
import sys


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


class ASCIIArtGenerator:
    """Generates ASCII art diagrams for CLI display."""
    
    @staticmethod
    def microservices() -> str:
        """Generate microservices architecture ASCII diagram."""
        return """
╔══════════════════════════════════════════════════════════════════╗
║                    MICROSERVICES ARCHITECTURE                     ║
╚══════════════════════════════════════════════════════════════════╝

                        ┌─────────────┐
                        │   Users     │
                        │  (Web/App)  │
                        └──────┬──────┘
                               │
                   ┌───────────▼───────────┐
                   │    Load Balancer      │
                   │      (nginx)          │
                   └───────────┬───────────┘
                               │
                   ┌───────────▼───────────┐
                   │     API Gateway       │
                   │   (Authentication)    │
                   └───────────┬───────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
   ┌────▼─────┐         ┌─────▼────┐          ┌─────▼────┐
   │  Auth    │         │  User    │          │  Order   │
   │ Service  │         │ Service  │          │ Service  │
   │  :3001   │         │  :3002   │          │  :3003   │
   └────┬─────┘         └─────┬────┘          └─────┬────┘
        │                     │                      │
        │              ┌──────▼──────┐               │
        │              │   Message   │               │
        └─────────────▶│    Queue    │◀──────────────┘
                       │  (RabbitMQ) │
                       └──────┬──────┘
                              │
                   ┌──────────▼──────────┐
                   │    Notification     │
                   │      Service        │
                   │       :3004         │
                   └──────────┬──────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
   ┌────▼─────┐         ┌────▼─────┐         ┌────▼─────┐
   │   Auth   │         │   User   │         │  Order   │
   │    DB    │         │    DB    │         │    DB    │
   │(Postgres)│         │ (MongoDB)│         │(Postgres)│
   └──────────┘         └──────────┘         └──────────┘

Key Benefits:
✅ Independent deployment
✅ Technology diversity
✅ Fault isolation
✅ Scalability per service

Challenges:
⚠️  Distributed system complexity
⚠️  Network latency
⚠️  Data consistency
⚠️  Testing complexity
"""

    @staticmethod
    def cicd_pipeline() -> str:
        """Generate CI/CD pipeline ASCII diagram."""
        return """
╔══════════════════════════════════════════════════════════════════╗
║                       CI/CD PIPELINE                              ║
╚══════════════════════════════════════════════════════════════════╝

Developer
    │
    │ git push
    ▼
┌─────────────────┐
│  Source Code    │
│   Repository    │
│     (GitHub)    │
└────────┬────────┘
         │ webhook triggers
         │
         ▼
┌─────────────────┐      ┌──────────────────┐
│   CI Server     │──────▶│  Build & Test    │
│   (Jenkins/     │      │  - Compile        │
│    CircleCI)    │      │  - Unit Tests     │
└────────┬────────┘      │  - Lint           │
         │               └──────────────────┘
         │ success
         ▼
┌─────────────────┐
│  Build Docker   │
│     Image       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Push to        │
│  Container      │
│  Registry       │
│  (Docker Hub)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────────┐
│  Deploy to      │      │  Run Integration │
│  Staging        │─────▶│      Tests       │
└────────┬────────┘      └──────────────────┘
         │                        │
         │ manual approval        │ pass
         ▼                        ▼
┌─────────────────┐      ┌──────────────────┐
│  Deploy to      │      │  Health Check    │
│  Production     │─────▶│  & Monitoring    │
│  (Blue/Green)   │      │  (Prometheus)    │
└─────────────────┘      └──────────────────┘

Pipeline Stages:
1️⃣  Source → Trigger build on commit
2️⃣  Build  → Compile & run unit tests
3️⃣  Test   → Integration & E2E tests
4️⃣  Deploy → Staging environment
5️⃣  Verify → Manual/automated approval
6️⃣  Release→ Production deployment
7️⃣  Monitor→ Health checks & rollback if needed
"""

    @staticmethod
    def kubernetes_cluster() -> str:
        """Generate Kubernetes cluster ASCII diagram."""
        return """
╔══════════════════════════════════════════════════════════════════╗
║                    KUBERNETES CLUSTER                             ║
╚══════════════════════════════════════════════════════════════════╝

                        ┌─────────────────┐
                        │  kubectl/API    │
                        │    Requests     │
                        └────────┬────────┘
                                 │
                    ┌────────────▼────────────┐
                    │    CONTROL PLANE        │
                    │   (Master Node)         │
                    ├─────────────────────────┤
                    │  • API Server           │
                    │  • Scheduler            │
                    │  • Controller Manager   │
                    │  • etcd (state store)   │
                    └────────────┬────────────┘
                                 │
        ┌────────────────────────┼────────────────────────┐
        │                        │                        │
┌───────▼────────┐      ┌───────▼────────┐      ┌───────▼────────┐
│  WORKER NODE 1 │      │  WORKER NODE 2 │      │  WORKER NODE 3 │
├────────────────┤      ├────────────────┤      ├────────────────┤
│ ┌────────────┐ │      │ ┌────────────┐ │      │ ┌────────────┐ │
│ │   kubelet  │ │      │ │   kubelet  │ │      │ │   kubelet  │ │
│ └────────────┘ │      │ └────────────┘ │      │ └────────────┘ │
│                │      │                │      │                │
│ ┌────────────┐ │      │ ┌────────────┐ │      │ ┌────────────┐ │
│ │ POD: web   │ │      │ │ POD: web   │ │      │ │ POD: api   │ │
│ │ ┌────────┐ │ │      │ │ ┌────────┐ │ │      │ │ ┌────────┐ │ │
│ │ │Container│││      │ │ │Container│││      │ │ │Container│││
│ │ │ nginx  │ │ │      │ │ │ nginx  │ │ │      │ │ │ node.js│ │ │
│ │ └────────┘ │ │      │ │ └────────┘ │ │      │ │ └────────┘ │ │
│ └────────────┘ │      │ └────────────┘ │      │ └────────────┘ │
│                │      │                │      │                │
│ ┌────────────┐ │      │ ┌────────────┐ │      │ ┌────────────┐ │
│ │ POD: cache │ │      │ │ POD: worker│ │      │ │ POD: db    │ │
│ │ ┌────────┐ │ │      │ │ ┌────────┐ │ │      │ │ ┌────────┐ │ │
│ │ │ redis  │ │ │      │ │ │ python │ │ │      │ │ │postgres│ │ │
│ │ └────────┘ │ │      │ │ └────────┘ │ │      │ │ └────────┘ │ │
│ └────────────┘ │      │ └────────────┘ │      │ └────────────┘ │
└────────────────┘      └────────────────┘      └────────────────┘

Services (LoadBalancers):
  web-service   → Distributes traffic to web pods
  api-service   → Routes to API pods
  cache-service → Internal Redis access

Kubernetes Concepts:
🎯 Pod       = Smallest deployable unit (1+ containers)
🔄 ReplicaSet= Ensures N pods are running
📦 Deployment= Manages ReplicaSets (rolling updates)
🌐 Service   = Stable network endpoint for pods
💾 Volume    = Persistent storage
"""

    @staticmethod
    def three_tier() -> str:
        """Generate 3-tier architecture ASCII diagram."""
        return """
╔══════════════════════════════════════════════════════════════════╗
║                    THREE-TIER ARCHITECTURE                        ║
╚══════════════════════════════════════════════════════════════════╝

┌──────────────────────────────────────────────────────────────────┐
│                      PRESENTATION TIER                            │
│                        (Frontend)                                 │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐          │
│  │   React     │    │   Angular   │    │  Mobile App │          │
│  │     SPA     │    │     SPA     │    │   (iOS/And) │          │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘          │
│         │                  │                   │                 │
└─────────┼──────────────────┼───────────────────┼─────────────────┘
          │                  │                   │
          └──────────────────┼───────────────────┘
                             │
                       HTTPS/REST API
                             │
┌────────────────────────────▼─────────────────────────────────────┐
│                       APPLICATION TIER                            │
│                      (Business Logic)                             │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────────────────────────────────────────┐         │
│  │          Load Balancer (nginx/HAProxy)              │         │
│  └────────────────────┬────────────────────────────────┘         │
│                       │                                           │
│       ┌───────────────┼───────────────┐                          │
│       │               │               │                          │
│  ┌────▼─────┐    ┌────▼─────┐   ┌────▼─────┐                    │
│  │ App      │    │ App      │   │ App      │                    │
│  │ Server 1 │    │ Server 2 │   │ Server 3 │                    │
│  │ (Node.js)│    │ (Node.js)│   │ (Node.js)│                    │
│  └────┬─────┘    └────┬─────┘   └────┬─────┘                    │
│       │               │               │                          │
│       └───────────────┼───────────────┘                          │
│                       │                                           │
└───────────────────────┼───────────────────────────────────────────┘
                        │
                   SQL Queries
                        │
┌───────────────────────▼───────────────────────────────────────────┐
│                         DATA TIER                                 │
│                       (Persistence)                               │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────────────────────────────────────────┐         │
│  │         Database Cluster (Primary/Replica)          │         │
│  └────────────────────┬────────────────────────────────┘         │
│                       │                                           │
│       ┌───────────────┼───────────────┐                          │
│       │               │               │                          │
│  ┌────▼─────┐    ┌────▼─────┐   ┌────▼─────┐                    │
│  │ Primary  │    │ Replica  │   │ Replica  │                    │
│  │   DB     │───▶│   DB 1   │   │   DB 2   │                    │
│  │(Postgres)│    │(Read only)   │(Read only)                    │
│  └──────────┘    └──────────┘   └──────────┘                    │
│       │                                                           │
│  ┌────▼──────────────────────────────────────────┐               │
│  │        Backup & Archive Storage               │               │
│  │              (Daily Backups)                  │               │
│  └───────────────────────────────────────────────┘               │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘

Separation of Concerns:
1️⃣  Presentation  = User interface (HTML/CSS/JS)
2️⃣  Application   = Business logic (API, processing)
3️⃣  Data          = Storage (Database, files)

Benefits:
✅ Scalability (scale each tier independently)
✅ Maintainability (clear boundaries)
✅ Security (network segmentation)
✅ Flexibility (swap components per tier)
"""

    @staticmethod
    def serverless() -> str:
        """Generate serverless architecture ASCII diagram."""
        return """
╔══════════════════════════════════════════════════════════════════╗
║                    SERVERLESS ARCHITECTURE                        ║
╚══════════════════════════════════════════════════════════════════╝

                        ┌─────────────┐
                        │   Client    │
                        │ (Web/Mobile)│
                        └──────┬──────┘
                               │ HTTPS
                               ▼
                    ┌──────────────────┐
                    │   CloudFront     │
                    │   (CDN/Cache)    │
                    └────────┬─────────┘
                             │
                    ┌────────▼─────────┐
                    │   API Gateway    │
                    │  (REST/GraphQL)  │
                    └────────┬─────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
   ┌────▼─────┐         ┌───▼──────┐        ┌───▼──────┐
   │ Lambda   │         │ Lambda   │        │ Lambda   │
   │ Function │         │ Function │        │ Function │
   │  (Auth)  │         │  (Users) │        │ (Orders) │
   └────┬─────┘         └────┬─────┘        └────┬─────┘
        │                    │                    │
        │              ┌─────▼─────┐              │
        │              │ DynamoDB  │              │
        └─────────────▶│  (NoSQL)  │◀─────────────┘
                       └─────┬─────┘
                             │
                    ┌────────▼─────────┐
                    │   EventBridge    │
                    │ (Event routing)  │
                    └────────┬─────────┘
                             │
                    ┌────────▼─────────┐
                    │     Lambda       │
                    │ (Notifications)  │
                    └────────┬─────────┘
                             │
                       ┌─────┴─────┐
                       │           │
                  ┌────▼────┐ ┌───▼────┐
                  │   SES   │ │  SNS   │
                  │ (Email) │ │ (SMS)  │
                  └─────────┘ └────────┘

Storage & Static Assets:
┌──────────────────────────────────────┐
│           S3 Bucket                  │
│  • Static Website Files (HTML/JS)   │
│  • User Uploads                      │
│  • Application Logs                  │
└──────────────────────────────────────┘

Serverless Benefits:
✅ No server management
✅ Automatic scaling
✅ Pay per execution
✅ Built-in high availability

Trade-offs:
⚠️  Cold start latency
⚠️  Vendor lock-in
⚠️  Debugging complexity
⚠️  Execution time limits
"""

    @staticmethod
    def event_driven() -> str:
        """Generate event-driven architecture ASCII diagram."""
        return """
╔══════════════════════════════════════════════════════════════════╗
║                   EVENT-DRIVEN ARCHITECTURE                       ║
╚══════════════════════════════════════════════════════════════════╝

Event Producers                Event Bus               Event Consumers
──────────────                ───────────              ───────────────

┌──────────────┐                                      ┌──────────────┐
│   User       │                                      │   Email      │
│   Service    │──┐                                ┌─▶│   Service    │
└──────────────┘  │                                │  └──────────────┘
                  │  user.created                  │
                  │                                │
┌──────────────┐  │     ┌────────────────────┐    │  ┌──────────────┐
│   Order      │  │     │                    │    │  │  Analytics   │
│   Service    │──┼────▶│   Event Bus        │────┼─▶│   Service    │
└──────────────┘  │     │   (Kafka/RabbitMQ) │    │  └──────────────┘
                  │     │                    │    │
                  │     └────────────────────┘    │
┌──────────────┐  │              │                │  ┌──────────────┐
│   Payment    │  │              │                └─▶│  Notification│
│   Service    │──┘              │                   │   Service    │
└──────────────┘                 │                   └──────────────┘
                                 │
                                 ▼
                        ┌────────────────┐
                        │  Event Store   │
                        │  (Audit Log)   │
                        └────────────────┘

Event Flow Example:

1. User places order
   Order Service publishes → "order.placed" event

2. Event Bus routes to subscribers:
   ┌─ Payment Service   → Process payment
   ├─ Inventory Service → Update stock
   ├─ Email Service     → Send confirmation
   └─ Analytics Service → Track metrics

3. Payment completes
   Payment Service publishes → "payment.completed"

4. Triggers next workflow:
   ┌─ Order Service     → Update order status
   └─ Shipping Service  → Initiate delivery

Event Types:
📨 Domain Events    = Business actions (order.placed)
🔔 Integration Events = System integration (payment.processed)
📊 Notification Events = User alerts (email.sent)

Benefits:
✅ Loose coupling
✅ Asynchronous processing
✅ Scalability
✅ Audit trail

Challenges:
⚠️  Eventual consistency
⚠️  Complex debugging
⚠️  Message ordering
⚠️  Duplicate handling
"""


class ArchitectureVisualizer:
    """
    Main visualizer class for generating architecture diagrams.
    """
    
    def __init__(self, mode=None):
        """Initialize the visualizer."""
        self.mode = mode
        self.ascii_generator = ASCIIArtGenerator()
        self._check_dependencies()
    
    def _check_dependencies(self) -> Dict[str, bool]:
        """Check if optional diagram libraries are available."""
        dependencies = {
            "diagrams": False,
            "graphviz": False,
        }
        
        try:
            import diagrams
            dependencies["diagrams"] = True
        except ImportError:
            pass
        
        try:
            result = subprocess.run(
                ["which", "dot"],
                capture_output=True,
                text=True
            )
            dependencies["graphviz"] = result.returncode == 0
        except Exception:
            pass
        
        return dependencies
    
    def generate(
        self,
        pattern: ArchitecturePattern,
        output_format: DiagramFormat = DiagramFormat.ASCII,
        output_path: Optional[str] = None,
        include_explanation: bool = True
    ) -> DiagramResult:
        """
        Generate an architecture diagram.
        
        Args:
            pattern: Architecture pattern to visualize
            output_format: Output format (ASCII, PNG, SVG, MERMAID)
            output_path: Path to save diagram (for PNG/SVG)
            include_explanation: Include educational explanation
            
        Returns:
            DiagramResult with diagram and metadata
        """
        if output_format == DiagramFormat.ASCII:
            return self._generate_ascii(pattern, include_explanation)
        elif output_format == DiagramFormat.MERMAID:
            return self._generate_mermaid(pattern, include_explanation)
        elif output_format in [DiagramFormat.PNG, DiagramFormat.SVG]:
            return self._generate_image(pattern, output_format, output_path, include_explanation)
        else:
            return DiagramResult(
                success=False,
                format=output_format,
                error=f"Unsupported format: {output_format}"
            )
    
    def _generate_ascii(
        self,
        pattern: ArchitecturePattern,
        include_explanation: bool
    ) -> DiagramResult:
        """Generate ASCII art diagram."""
        ascii_generators = {
            ArchitecturePattern.MICROSERVICES: self.ascii_generator.microservices,
            ArchitecturePattern.CICD_PIPELINE: self.ascii_generator.cicd_pipeline,
            ArchitecturePattern.KUBERNETES: self.ascii_generator.kubernetes_cluster,
            ArchitecturePattern.THREE_TIER: self.ascii_generator.three_tier,
            ArchitecturePattern.SERVERLESS: self.ascii_generator.serverless,
            ArchitecturePattern.EVENT_DRIVEN: self.ascii_generator.event_driven,
        }
        
        generator = ascii_generators.get(pattern)
        if not generator:
            return DiagramResult(
                success=False,
                format=DiagramFormat.ASCII,
                error=f"No ASCII generator for pattern: {pattern.value}"
            )
        
        ascii_output = generator()
        explanation = self._get_explanation(pattern) if include_explanation else ""
        
        return DiagramResult(
            success=True,
            format=DiagramFormat.ASCII,
            ascii_output=ascii_output,
            explanation=explanation
        )
    
    def _generate_mermaid(
        self,
        pattern: ArchitecturePattern,
        include_explanation: bool
    ) -> DiagramResult:
        """Generate Mermaid diagram syntax."""
        mermaid_templates = {
            ArchitecturePattern.MICROSERVICES: """
graph TB
    Users[Users] --> LB[Load Balancer]
    LB --> Gateway[API Gateway]
    Gateway --> Auth[Auth Service]
    Gateway --> User[User Service]
    Gateway --> Order[Order Service]
    Auth --> AuthDB[(Auth DB)]
    User --> UserDB[(User DB)]
    Order --> OrderDB[(Order DB)]
    User --> Queue[Message Queue]
    Order --> Queue
    Queue --> Notify[Notification Service]
""",
            ArchitecturePattern.CICD_PIPELINE: """
graph LR
    Dev[Developer] -->|git push| Repo[Git Repository]
    Repo -->|webhook| CI[CI Server]
    CI --> Build[Build & Test]
    Build --> Docker[Build Image]
    Docker --> Registry[Container Registry]
    Registry --> Staging[Deploy Staging]
    Staging --> Tests[Integration Tests]
    Tests -->|approval| Prod[Deploy Production]
    Prod --> Monitor[Monitoring]
""",
            ArchitecturePattern.THREE_TIER: """
graph TB
    subgraph Presentation
        Web[Web App]
        Mobile[Mobile App]
    end
    subgraph Application
        LB[Load Balancer]
        App1[App Server 1]
        App2[App Server 2]
        App3[App Server 3]
    end
    subgraph Data
        Primary[(Primary DB)]
        Replica1[(Replica 1)]
        Replica2[(Replica 2)]
    end
    Web --> LB
    Mobile --> LB
    LB --> App1
    LB --> App2
    LB --> App3
    App1 --> Primary
    App2 --> Primary
    App3 --> Primary
    Primary --> Replica1
    Primary --> Replica2
""",
        }
        
        mermaid_code = mermaid_templates.get(pattern, "graph TB\n    A[No template available]")
        explanation = self._get_explanation(pattern) if include_explanation else ""
        
        return DiagramResult(
            success=True,
            format=DiagramFormat.MERMAID,
            ascii_output=mermaid_code,
            explanation=explanation
        )
    
    def _generate_image(
        self,
        pattern: ArchitecturePattern,
        output_format: DiagramFormat,
        output_path: Optional[str],
        include_explanation: bool
    ) -> DiagramResult:
        """Generate PNG/SVG diagram using diagrams library."""
        deps = self._check_dependencies()
        
        if not deps["diagrams"]:
            return DiagramResult(
                success=False,
                format=output_format,
                error="diagrams library not installed. Run: pip install diagrams"
            )
        
        if not deps["graphviz"]:
            return DiagramResult(
                success=False,
                format=output_format,
                error="graphviz not installed. Run: apt-get install graphviz (or brew install graphviz on Mac)"
            )
        
        try:
            from diagrams import Diagram, Cluster, Edge
            from diagrams.onprem.client import Users
            from diagrams.onprem.compute import Server
            from diagrams.onprem.database import PostgreSQL, MongoDB
            from diagrams.onprem.network import Nginx
            from diagrams.onprem.queue import RabbitMQ
            
            # Set output path
            if not output_path:
                output_path = f"{pattern.value}_architecture"
            
            # Remove extension if provided (diagrams adds it)
            output_path = output_path.replace('.png', '').replace('.svg', '')
            
            # Generate based on pattern
            if pattern == ArchitecturePattern.MICROSERVICES:
                with Diagram(
                    "Microservices Architecture",
                    filename=output_path,
                    show=False,
                    direction="TB"
                ):
                    users = Users("Users")
                    lb = Nginx("Load Balancer")
                    gateway = Server("API Gateway")
                    
                    with Cluster("Services"):
                        auth = Server("Auth Service")
                        user_svc = Server("User Service")
                        order_svc = Server("Order Service")
                        services = [auth, user_svc, order_svc]
                    
                    queue = RabbitMQ("Message Queue")
                    notify = Server("Notification")
                    
                    with Cluster("Databases"):
                        auth_db = PostgreSQL("Auth DB")
                        user_db = MongoDB("User DB")
                        order_db = PostgreSQL("Order DB")
                    
                    users >> lb >> gateway
                    gateway >> services
                    auth >> auth_db
                    user_svc >> user_db
                    order_svc >> order_db
                    services >> queue >> notify
            
            else:
                return DiagramResult(
                    success=False,
                    format=output_format,
                    error=f"Image generation not yet implemented for: {pattern.value}"
                )
            
            # Diagrams library creates .png by default
            generated_file = f"{output_path}.png"
            
            explanation = self._get_explanation(pattern) if include_explanation else ""
            
            return DiagramResult(
                success=True,
                format=output_format,
                filepath=generated_file,
                explanation=explanation
            )
            
        except Exception as e:
            return DiagramResult(
                success=False,
                format=output_format,
                error=f"Error generating diagram: {str(e)}"
            )
    
    def _get_explanation(self, pattern: ArchitecturePattern) -> str:
        """Get educational explanation for architecture pattern."""
        explanations = {
            ArchitecturePattern.MICROSERVICES: """
🎓 MICROSERVICES ARCHITECTURE EXPLAINED

What is it?
Breaking your application into small, independent services that each do ONE thing well.
Think of it like a restaurant: instead of one person doing everything (cooking, serving,
cleaning), you have specialists - a chef, a waiter, a dishwasher. Each is independent
and can be replaced or scaled without affecting the others.

When to use:
✅ Large, complex applications
✅ Need to scale different parts independently
✅ Different teams working on different features
✅ Want to use different technologies per service

When NOT to use:
❌ Small applications (overkill)
❌ Team not familiar with distributed systems
❌ Simple CRUD apps
❌ Need for strong consistency across all data

Real-world examples:
- Netflix (600+ microservices)
- Amazon (service-oriented architecture)
- Uber (food, rides, payments all separate)
""",
            ArchitecturePattern.CICD_PIPELINE: """
🎓 CI/CD PIPELINE EXPLAINED

What is it?
Continuous Integration/Continuous Deployment - automatically testing and deploying
code changes. Think of it like a factory assembly line: code goes in one end,
tests run automatically, and working software comes out the other end.

Pipeline Stages:
1. Source: Developer pushes code to Git
2. Build: Compile code, install dependencies
3. Test: Run automated tests
4. Package: Create deployable artifact (Docker image)
5. Deploy: Push to staging, then production
6. Monitor: Track health and rollback if needed

Benefits:
✅ Faster releases (hours instead of weeks)
✅ Fewer bugs reach production
✅ Consistent deployment process
✅ Quick rollback if issues arise

Best Practices:
- Keep builds fast (<10 minutes)
- Test everything automatically
- Deploy to staging first
- Use blue/green deployments
- Monitor actively post-deployment
""",
            ArchitecturePattern.THREE_TIER: """
🎓 THREE-TIER ARCHITECTURE EXPLAINED

What is it?
Separating your application into three logical layers. Think of it like a restaurant:
- Presentation (dining area): What customers see and interact with
- Application (kitchen): Where the work happens
- Data (pantry): Where ingredients/data is stored

The Three Tiers:
1️⃣  Presentation Tier
   - User interface (web, mobile)
   - Handles user interactions
   - No business logic

2️⃣  Application Tier
   - Business logic and rules
   - Processes requests
   - Coordinates between presentation and data

3️⃣  Data Tier
   - Database and file storage
   - Data persistence
   - Backups and recovery

Why use it?
✅ Clear separation of concerns
✅ Easy to maintain and update
✅ Security (layers can be firewalled)
✅ Scale tiers independently

Classic use case:
Traditional web applications, enterprise systems, e-commerce platforms
""",
            ArchitecturePattern.SERVERLESS: """
🎓 SERVERLESS ARCHITECTURE EXPLAINED

What is it?
You write code (functions), and the cloud provider runs it for you. No servers to
manage! Think of it like using Uber instead of owning a car - you only pay when
you use it, and someone else handles all the maintenance.

Key Components:
- Lambda Functions: Your code that runs on-demand
- API Gateway: Routes requests to functions
- Storage (S3): Static files and uploads
- Database (DynamoDB): Data storage
- Events: Triggers that start functions

Benefits:
✅ Zero server management
✅ Automatic scaling (0 to millions)
✅ Pay only for execution time
✅ Built-in high availability

Challenges:
⚠️  Cold starts (first request slower)
⚠️  15-minute execution limit (AWS Lambda)
⚠️  Harder to debug
⚠️  Vendor lock-in

Best for:
- APIs with sporadic traffic
- Event-driven workflows
- Scheduled tasks
- Real-time file processing
""",
            ArchitecturePattern.EVENT_DRIVEN: """
🎓 EVENT-DRIVEN ARCHITECTURE EXPLAINED

What is it?
Services communicate by publishing and subscribing to events. Think of it like
a notification system: when something happens (event), interested parties get
notified automatically without directly calling each other.

How it works:
1. Service A does something (e.g., user signs up)
2. Service A publishes an event: "user.created"
3. Event Bus routes event to subscribers
4. Services B, C, D all receive and react independently

Example Flow:
User places order →
   ├─ Order Service: Create order record
   ├─ Payment Service: Charge credit card
   ├─ Inventory Service: Reserve items
   ├─ Email Service: Send confirmation
   └─ Analytics Service: Track conversion

Benefits:
✅ Loose coupling (services don't know about each other)
✅ Easy to add new features (just subscribe to events)
✅ Asynchronous (don't wait for responses)
✅ Scalable

Challenges:
⚠️  Eventual consistency (not immediate)
⚠️  Harder to trace failures
⚠️  Duplicate events possible
⚠️  Message ordering complexit

Best for:
- Complex workflows with many steps
- Systems that need to scale independently
- When adding features frequently
"""
        }
        
        return explanations.get(pattern, "")
    
    def list_available_patterns(self) -> List[Tuple[str, str]]:
        """List all available architecture patterns."""
        return [
            (pattern.value, pattern.value.replace('_', ' ').title())
            for pattern in ArchitecturePattern
        ]

    # ------------------------------------------------------------------
    # 🧠 Concept Visual Models (For explain command learning topics)
    # ------------------------------------------------------------------

    def generate_concept_visual(self, topic: str) -> DiagramResult:
        """
        Generate a visual model for general DevOps concepts
        (used by 'explain' command, not architecture design).
        """
        topic = topic.lower()

        if "linux" in topic:
            return DiagramResult(
                success=True,
                format=DiagramFormat.ASCII,
                ascii_output=self._linux_visual(),
                explanation="🧠 Visual model of how Linux is structured internally."
            )

        if "container" in topic:
            return DiagramResult(
                success=True,
                format=DiagramFormat.ASCII,
                ascii_output=self._container_visual(),
                explanation="🧠 Visual model showing how containers isolate applications."
            )

        return DiagramResult(
            success=False,
            format=DiagramFormat.ASCII,
            error="No visual model available for this topic yet."
        )

    def _linux_visual(self) -> str:
        return """
╔══════════════════════════════════════════════════════════════════╗
║                     LINUX SYSTEM MODEL                           ║
╚══════════════════════════════════════════════════════════════════╝

User
  │
  ▼
Shell (bash / zsh)
  │
  ▼
Linux Kernel
  │
  ▼
Hardware (CPU, RAM, Disk)

Filesystem Structure:
/
├── home   → user files
├── etc    → configuration
├── var    → logs & runtime data
├── usr    → applications
└── bin    → system commands

Key Idea:
Everything in Linux is a file.
The kernel controls access to hardware.
"""

    def _container_visual(self) -> str:
        return """
╔══════════════════════════════════════════════════════════════════╗
║                     CONTAINERIZATION MODEL                       ║
╚══════════════════════════════════════════════════════════════════╝

                 Host OS
  ┌─────────────────────────────────────────────┐
  │               Docker Engine                 │
  │                                             │
  │  ┌──────────────┐  ┌──────────────┐        │
  │  │  Container 1 │  │  Container 2 │        │
  │  │  App + Libs  │  │  App + Libs  │        │
  │  └──────────────┘  └──────────────┘        │
  │                                             │
  └─────────────────────────────────────────────┘

Each container:
- Has its own filesystem
- Has isolated processes
- Shares the host kernel

Image → Blueprint
Container → Running instance
Registry → Storage for images
"""


def format_diagram_result(result: DiagramResult, mode=None) -> str:
    """Format diagram result for display."""
    output = []
    
    if not result.success:
        output.append("❌ Failed to generate diagram")
        output.append(f"Error: {result.error}")
        return "\n".join(output)
    
    # Show ASCII output if available
    if result.ascii_output:
        output.append(result.ascii_output)
    
    # Show file path if generated
    if result.filepath:
        output.append(f"\n✅ Diagram saved to: {result.filepath}")
    
    # Add explanation
    if result.explanation:
        output.append("\n" + "=" * 70)
        output.append(result.explanation)
    
    return "\n".join(output)


# Example usage
if __name__ == "__main__":
    visualizer = ArchitectureVisualizer()
    
    print("🎨 Testing ArchitectureVisualizer Module\n")
    print("=" * 70)
    
    # Test ASCII generation
    print("\n1. Generating Microservices Architecture (ASCII)...")
    result = visualizer.generate(
        ArchitecturePattern.MICROSERVICES,
        DiagramFormat.ASCII,
        include_explanation=True
    )
    print(format_diagram_result(result))
    
    print("\n" + "=" * 70)
    print("\n2. Available Patterns:")
    for value, name in visualizer.list_available_patterns():
        print(f"   - {name} ({value})")
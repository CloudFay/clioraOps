"""
Architecture Pattern Explanations for ArchitectureVisualizer

Contains detailed educational explanations for each architecture pattern.
This module is separated to keep the main visualizer module focused on
diagram generation logic.
"""

from typing import Dict
from clioraOps_cli.features.models import ArchitecturePattern


# Educational explanations for each architecture pattern
ARCHITECTURE_EXPLANATIONS: Dict[ArchitecturePattern, str] = {
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
⚠️  Message ordering complexity

Best for:
- Complex workflows with many steps
- Systems that need to scale independently
- When adding features frequently
""",
    ArchitecturePattern.KUBERNETES: """
🎓 KUBERNETES ARCHITECTURE EXPLAINED

What is it?
An orchestration platform for automatically deploying, scaling, and managing
containerized applications. Think of it as a smart container manager that decides
where containers should run.

Core Concepts:
- Cluster: Group of machines running containers
- Pod: Smallest unit (usually one container)
- Deployment: Declares desired state
- Service: Network abstraction for pods
- Namespace: Virtual cluster for multi-tenancy

Key Benefits:
✅ Automatic container scheduling
✅ Self-healing (restarts failed containers)
✅ Rolling updates with zero downtime
✅ Horizontal scaling
✅ Load balancing

When to use:
- Large-scale applications
- Need for automatic healing and scaling
- Microservices architecture
- Complex deployment requirements

Learning curve:
⚠️  Steep learning curve
⚠️  Operational complexity
⚠️  Resource requirements

Best for:
- Enterprise applications
- Microservices at scale
- Teams with DevOps expertise
""",
}


def get_explanation(pattern: ArchitecturePattern) -> str:
    """
    Get educational explanation for an architecture pattern.
    
    Args:
        pattern: ArchitecturePattern enum value
        
    Returns:
        Explanation string, or empty string if pattern not found
    """
    return ARCHITECTURE_EXPLANATIONS.get(pattern, "")

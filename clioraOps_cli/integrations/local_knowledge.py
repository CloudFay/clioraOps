"""
Local knowledge base for ClioraOps fallback responses.

Provides intelligent template-based responses when cloud AI providers are unavailable.
"""

from enum import Enum
from typing import Optional, Dict, List
import re


class PromptCategory(Enum):
    """Categories of user prompts."""
    EXPLAIN = "explain"
    DEBUG = "debug"
    GENERATE = "generate"
    DESIGN = "design"
    LEARN = "learn"
    HELP = "help"
    GENERAL = "general"


class LocalKnowledgeBase:
    """
    Local knowledge base with template responses for common queries.
    Provides intelligent fallback when cloud providers are unavailable.
    """
    
    def __init__(self):
        self.knowledge = {
            "docker": self._docker_knowledge(),
            "kubernetes": self._kubernetes_knowledge(),
            "ci_cd": self._ci_cd_knowledge(),
            "terraform": self._terraform_knowledge(),
            "aws": self._aws_knowledge(),
            "devops": self._devops_knowledge(),
        }
    
    def categorize_prompt(self, prompt: str) -> PromptCategory:
        """Categorize user prompt to determine response type."""
        prompt_lower = prompt.lower().strip()
        
        # Explain/Learn patterns
        if any(word in prompt_lower for word in ["explain", "what is", "how does", "tell me about"]):
            return PromptCategory.EXPLAIN
        
        # Debug patterns
        if any(word in prompt_lower for word in ["debug", "error", "fix", "why is", "problem", "issue", "wrong"]):
            return PromptCategory.DEBUG
        
        # Generate/Code patterns
        if any(word in prompt_lower for word in ["generate", "create", "write", "build", "code", "script"]):
            return PromptCategory.GENERATE
        
        # Design/Architecture patterns
        if any(word in prompt_lower for word in ["design", "architect", "structure", "how should", "best practice"]):
            return PromptCategory.DESIGN
        
        # Learn patterns
        if any(word in prompt_lower for word in ["learn", "tutorial", "guide", "steps", "how to"]):
            return PromptCategory.LEARN
        
        # Help patterns
        if any(word in prompt_lower for word in ["help", "support", "assist", "guide me"]):
            return PromptCategory.HELP
        
        return PromptCategory.GENERAL
    
    def extract_topic(self, prompt: str) -> Optional[str]:
        """Extract main topic from prompt."""
        prompt_lower = prompt.lower()
        
        for topic in self.knowledge.keys():
            if topic in prompt_lower:
                return topic
        
        return None
    
    def get_response(self, prompt: str, system_prompt: str = "") -> str:
        """
        Generate intelligent response based on prompt.
        
        Args:
            prompt: User's input prompt
            system_prompt: System prompt providing context (beginner/architect mode)
        
        Returns:
            Intelligent template-based response
        """
        category = self.categorize_prompt(prompt)
        topic = self.extract_topic(prompt)
        
        # Try to get specific knowledge response
        if topic and topic in self.knowledge:
            response = self._get_topic_response(
                topic,
                prompt,
                category,
                system_prompt
            )
            if response:
                return response
        
        # Fall back to generic category response
        return self._get_category_response(prompt, category, system_prompt)
    
    def _get_topic_response(
        self,
        topic: str,
        prompt: str,
        category: PromptCategory,
        system_prompt: str
    ) -> Optional[str]:
        """Get response for a specific topic."""
        knowledge = self.knowledge.get(topic, {})
        
        if category == PromptCategory.EXPLAIN:
            return knowledge.get("explain")
        elif category == PromptCategory.DEBUG:
            return knowledge.get("debug")
        elif category == PromptCategory.GENERATE:
            return knowledge.get("generate")
        elif category == PromptCategory.DESIGN:
            return knowledge.get("design")
        elif category == PromptCategory.LEARN:
            return knowledge.get("learn")
        
        return knowledge.get("overview")
    
    def _get_category_response(
        self,
        prompt: str,
        category: PromptCategory,
        system_prompt: str
    ) -> str:
        """Get generic response based on category."""
        
        is_beginner = "beginner" in system_prompt.lower()
        
        if category == PromptCategory.EXPLAIN:
            return self._generic_explain(prompt, is_beginner)
        elif category == PromptCategory.DEBUG:
            return self._generic_debug(prompt, is_beginner)
        elif category == PromptCategory.GENERATE:
            return self._generic_generate(prompt, is_beginner)
        elif category == PromptCategory.DESIGN:
            return self._generic_design(prompt, is_beginner)
        elif category == PromptCategory.LEARN:
            return self._generic_learn(prompt, is_beginner)
        elif category == PromptCategory.HELP:
            return self._generic_help(is_beginner)
        else:
            return self._generic_response(prompt, is_beginner)
    
    # ===== KNOWLEDGE BASES =====
    
    def _docker_knowledge(self) -> Dict:
        return {
            "explain": """
**Docker: Containerization Made Simple** 🐳

Think of Docker like shipping containers. Instead of shipping physical goods, Docker containers ship your code with everything it needs:
- Application code
- Runtime
- Dependencies
- System libraries

**Why Docker?**
- **Consistency**: "Works on my machine" problem solved ✅
- **Isolation**: Apps don't interfere with each other
- **Portability**: Same container runs on dev, test, and production
- **Efficiency**: Lighter than VMs, faster to start

**Key Concepts:**
- **Image**: Blueprint for a container (like a recipe)
- **Container**: Running instance of an image (like baked cake)
- **Dockerfile**: Instructions to build an image
- **Registry**: Place to store/share images (Docker Hub)

**Quick Start:**
```bash
docker run -d -p 8080:80 nginx
```
This starts a web server that's accessible on port 8080!
""",
            "debug": """
**Common Docker Issues & Fixes** 🔧

1. **"Cannot connect to Docker daemon"**
   - Docker service not running: `sudo systemctl start docker`
   - Permission issue: `sudo usermod -aG docker $USER`

2. **"Port already in use"**
   - Kill existing container: `docker stop <container_id>`
   - Or use different port: `docker run -p 8081:80 ...`

3. **Image won't build**
   - Check Dockerfile syntax
   - Ensure base image exists: `docker pull <image>`
   - Build with verbose output: `docker build --verbose ...`

4. **Container exits immediately**
   - Check logs: `docker logs <container_id>`
   - Usually means app crashed
""",
            "learn": """
**Learning Docker Step by Step** 📚

1. **Day 1: Basics**
   - Install Docker
   - Run first container: `docker run hello-world`
   - Explore images: `docker images`

2. **Day 2: Containerize an app**
   - Write a Dockerfile
   - Build: `docker build -t myapp .`
   - Run your image: `docker run myapp`

3. **Day 3: Multi-container apps**
   - Learn Docker Compose
   - Define services in docker-compose.yml
   - Start stack: `docker-compose up`

4. **Day 4+: Production**
   - Push to registry
   - Container networking
   - Volume management
   - Health checks
""",
            "design": """
**Docker Architecture Best Practices** 🏗️

1. **Dockerfile Best Practices**
   - Use specific base image versions (not `latest`)
   - Keep layers small and organized
   - Use multi-stage builds for smaller images
   - Always include health checks

2. **Image Sizing**
   - Use minimal base images (Alpine, distroless)
   - Remove build dependencies
   - Optimize layer caching

3. **Security**
   - Don't run as root
   - Scan images for vulnerabilities
   - Keep base images updated
   - Use private registries for sensitive apps

4. **Performance**
   - Use health checks
   - Set resource limits
   - Configure proper logging
""",
            "generate": "**Docker Code Generation** - Please ask for specific Docker code or Dockerfile examples!",
            "overview": "Docker is a containerization platform. Ask me to explain, debug, or generate Docker code!"
        }
    
    def _kubernetes_knowledge(self) -> Dict:
        return {
            "explain": """
**Kubernetes: Container Orchestration** ⚙️

Kubernetes (K8s) is like an orchestra conductor for containers. Instead of managing containers manually, Kubernetes:
- Automatically deploys containers
- Restarts failed containers
- Scales up/down based on demand
- Manages updates with zero downtime

**Why Kubernetes?**
- **Scalability**: Handle millions of requests by scaling pods
- **Resilience**: Self-healing and automatic recovery
- **Load Balancing**: Distributes traffic automatically
- **Updates**: Rolling deployments without downtime

**Key Concepts:**
- **Pod**: Smallest deployable unit (usually 1 container)
- **Deployment**: Manages pod replicas
- **Service**: Exposes pods to network
- **Namespace**: Virtual clusters within cluster

**Quick Example:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
      - name: app
        image: myapp:1.0
```
""",
            "debug": """
**Common Kubernetes Issues** 🔧

1. **Pod CrashLoopBackOff**
   - App keeps crashing
   - Check logs: `kubectl logs <pod>`
   - Verify image: `kubectl describe pod <pod>`

2. **ImagePullBackOff**
   - Image not found or accessible
   - Check image name and registry credentials
   - Verify registry access: `kubectl describe pod <pod>`

3. **Service not reachable**
   - Check service selector matches pod labels
   - Verify service type (ClusterIP vs LoadBalancer)
   - Test from pod: `kubectl exec -it <pod> -- curl service`

4. **Node NotReady**
   - Node hardware/networking issue
   - Check node: `kubectl describe node <node>`
   - Check kubelet: `systemctl status kubelet`
""",
            "learn": """
**Learning Kubernetes** 📚

1. **Week 1: Core Concepts**
   - Pods, Deployments, Services
   - Run local cluster (minikube or kind)
   - Deploy first application

2. **Week 2: Storage & Config**
   - ConfigMaps and Secrets
   - Persistent Volumes
   - StatefulSets for databases

3. **Week 3: Networking**
   - Services (ClusterIP, NodePort, LoadBalancer)
   - Ingress for external access
   - Network policies

4. **Week 4+: Production**
   - Helm for package management
   - Monitoring with Prometheus
   - Logging with ELK/Loki
   - Security policies
""",
            "design": """
**Kubernetes Architecture Best Practices** 🏗️

1. **Deployment Strategy**
   - Use declarative manifests (YAML)
   - Version control all configs
   - Separate dev/staging/prod namespaces

2. **Resource Management**
   - Always set resource requests/limits
   - Use HorizontalPodAutoscaler for scaling
   - Monitor resource usage

3. **High Availability**
   - Multi-replica deployments
   - Anti-affinity rules
   - Pod disruption budgets
   - Health checks (readiness/liveness)

4. **Security**
   - Network policies
   - RBAC for access control
   - Pod security policies
   - Scan container images
""",
            "overview": "Kubernetes orchestrates containers at scale. Ask to explain, debug, or design K8s architectures!"
        }
    
    def _ci_cd_knowledge(self) -> Dict:
        return {
            "explain": """
**CI/CD: Continuous Integration & Deployment** 🚀

CI/CD automates the journey from code to production:

**Continuous Integration (CI):**
- Developer pushes code
- Automated tests run
- Code quality checks
- Build artifacts created

**Continuous Deployment (CD):**
- Automated tests pass ✅
- Code auto-deployed to staging
- Additional tests
- Auto-deployed to production

**Why CI/CD?**
- Catch bugs early
- Faster releases (daily vs monthly)
- Less manual work
- Consistent deployments
- Rollback capability

**Common Tools:**
- GitHub Actions, GitLab CI, Jenkins
- Testing: pytest, jest, go test
- Deployment: ArgoCD, Spinnaker, Jenkins
""",
            "debug": """
**Common CI/CD Issues** 🔧

1. **Build failures**
   - Check test output logs
   - Verify dependencies installed
   - Check environment variables

2. **Deployment failures**
   - Insufficient permissions
   - Missing secrets/credentials
   - Image not built/pushed
   - Health check failures

3. **Slow pipelines**
   - Parallelize tests
   - Cache dependencies
   - Optimize Docker builds
   - Use smaller base images
""",
            "learn": """
**Getting Started with CI/CD** 📚

1. **Setup source control**
   - Git repository
   - Branch strategy (main, develop)

2. **Add CI**
   - Create pipeline file (.github/workflows/ci.yml or .gitlab-ci.yml)
   - Add test stage
   - Add build stage

3. **Add CD**
   - Add deployment stage
   - Deploy to staging first
   - Manual approval for production

4. **Mature**
   - Comprehensive testing
   - Security scanning
   - Performance testing
   - Automated rollback
""",
            "overview": "CI/CD automates code testing and deployment. Ask to explain, debug, or set up a pipeline!"
        }
    
    def _terraform_knowledge(self) -> Dict:
        return {
            "explain": """
**Terraform: Infrastructure as Code** 🏗️

Terraform lets you write code to define infrastructure:
- VMs, databases, networks
- Defined in .tf files
- Version controlled
- Reproducible across environments

**Key Benefits:**
- Declarative (describe what you want)
- Idempotent (safe to run multiple times)
- Version control your infrastructure
- Easy to replicate across clouds
""",
            "overview": "Terraform manages infrastructure as code. Ask for specific Terraform examples or concepts!"
        }
    
    def _aws_knowledge(self) -> Dict:
        return {
            "explain": """
**AWS: Amazon Web Services** ☁️

AWS is a cloud platform with 200+ services:

**Core Services:**
- **EC2**: Virtual machines
- **S3**: Object storage
- **RDS**: Managed databases
- **Lambda**: Serverless functions
- **VPC**: Networking

**DevOps Services:**
- CodePipeline: CI/CD
- CloudFormation: IaC
- ECS/EKS: Container orchestration
- CloudWatch: Monitoring

Start with: EC2 for compute, S3 for storage, RDS for databases.
""",
            "overview": "AWS is a cloud platform. Ask for specific AWS service explanations!"
        }
    
    def _devops_knowledge(self) -> Dict:
        return {
            "explain": """
**DevOps: Culture & Practices** 👥

DevOps combines development and operations:

**Key Principles:**
- **Collaboration**: Dev and Ops work together
- **Automation**: Automate repetitive tasks
- **Measurement**: Monitor everything
- **Sharing**: Share knowledge and tools

**Core Practices:**
- Continuous Integration (automated testing)
- Continuous Deployment (automated releases)
- Infrastructure as Code (manage infra like code)
- Monitoring & Logging (observability)
- On-call & Incident Response

**Tools & Technologies:**
- Version control: Git
- CI/CD: GitHub Actions, GitLab CI, Jenkins
- Containers: Docker, Kubernetes
- IaC: Terraform, CloudFormation
- Monitoring: Prometheus, Grafana, DataDog
""",
            "overview": "DevOps is a culture of automation and collaboration. Ask specific questions about practices!"
        }
    
    # ===== GENERIC RESPONSES =====
    
    def _generic_explain(self, prompt: str, is_beginner: bool) -> str:
        if is_beginner:
            return f"""
**Let me explain** that in simple terms! 🌱

I notice you're asking about: {prompt[:50]}...

Since I don't have a detailed knowledge base entry for this specific topic, here's what I recommend:

1. **Ask more specific**: Try "explain docker" or "explain kubernetes"
2. **Use AI brain**: Connect Gemini API for unlimited detailed explanations
3. **Available topics**: Docker, Kubernetes, CI/CD, Terraform, AWS, DevOps

Would you like me to explain one of these topics in detail? 🚀
"""
        else:
            return f"""
**Technical Explanation Request**

Your query: {prompt[:50]}...

Available knowledge base topics:
- Docker & containerization
- Kubernetes orchestration
- CI/CD pipelines
- Terraform infrastructure
- AWS services
- DevOps practices

For detailed technical analysis, please:
1. Ask about a specific topic
2. Or connect Gemini API for in-depth analysis

Which topic would you like to explore? 🔍
"""
    
    def _generic_debug(self, prompt: str, is_beginner: bool) -> str:
        if is_beginner:
            return f"""
**Let me help you debug!** 🔧

You mentioned: {prompt[:50]}...

To help you effectively, I need:
1. **Error message**: Exact error text
2. **What you were doing**: Command or action
3. **System info**: OS, Docker version, etc.

Try asking like:
- "debug docker connection refused"
- "debug kubernetes pod crash"
- "debug ci/cd build failure"

Or connect Gemini API for real-time debugging assistance! 🚀
"""
        else:
            return f"""
**Debug Request**

Issue: {prompt[:50]}...

To provide root cause analysis, please provide:
1. Error logs/stack trace
2. Command/configuration context
3. Environment details

Available debug knowledge:
- Docker daemon/image issues
- Kubernetes pod failures
- CI/CD pipeline failures

Which system would you like to debug? 🔍
"""
    
    def _generic_generate(self, prompt: str, is_beginner: bool) -> str:
        return f"""
**Code Generation**

Your request: {prompt[:50]}...

I can help generate:
- Dockerfiles
- Kubernetes manifests
- CI/CD pipeline configs
- Terraform modules
- Shell scripts

For detailed code generation, please:
1. Connect Gemini API for full code
2. Or ask specific questions about patterns

Which type of code would you like? 💻
"""
    
    def _generic_design(self, prompt: str, is_beginner: bool) -> str:
        return f"""
**Architecture Design**

Your question: {prompt[:50]}...

I can discuss:
- System architecture patterns
- Scalability approaches
- High availability strategies
- Security best practices
- Cost optimization

For detailed architectural guidance:
1. Connect Gemini API for analysis
2. Or ask about specific patterns

What's your design question? 🏗️
"""
    
    def _generic_learn(self, prompt: str, is_beginner: bool) -> str:
        return f"""
**Learning Path**

Topic: {prompt[:50]}...

I can guide you through:
- Docker basics → advanced
- Kubernetes fundamentals → production
- CI/CD setup → optimization
- DevOps practices

To get started:
1. Ask "learn docker"
2. Or connect Gemini API for interactive learning

What would you like to learn? 📚
"""
    
    def _generic_help(self, is_beginner: bool) -> str:
        if is_beginner:
            return """
**🌱 Beginner Help Menu**

Try these commands:
- `explain docker` - Learn what Docker is
- `explain kubernetes` - Understand container orchestration
- `learn ci_cd` - Step-by-step CI/CD guide
- `debug <error>` - Fix common errors

**AI Brain Setup:**
`setup ai gemini YOUR_API_KEY`
(Free key: https://aistudio.google.com/app/apikey)

Or install Ollama for offline AI:
https://ollama.com

What would you like to explore? 🚀
"""
        else:
            return """
**🏗️ Architect Help Menu**

Available features:
- `explain <topic>` - Technical explanations
- `design <architecture>` - System design discussions
- `generate <code>` - Code generation
- `threat <system>` - Threat modeling
- `debug <error>` - Root cause analysis

**AI Brain Setup:**
`setup ai gemini <key>`
or
`switch brain ollama`

What would you like to do? 🔍
"""
    
    def _generic_response(self, prompt: str, is_beginner: bool) -> str:
        if is_beginner:
            return f"""
**Got your question!** 🌱

You asked: {prompt[:50]}...

I can help with:
- **Explaining** concepts (Docker, Kubernetes, etc.)
- **Learning** step-by-step guides
- **Debugging** common errors
- **Generating** DevOps code

To unlock full capabilities, connect an AI brain:
`setup ai gemini YOUR_KEY`

Or ask me about specific topics! What interests you? 🚀
"""
        else:
            return f"""
**Query Received**

Request: {prompt[:50]}...

I'm ready to assist with:
- Technical explanations
- System design
- Code generation
- Troubleshooting
- Best practices

For enhanced responses, connect Gemini:
`setup ai gemini <key>`

What can I help you with? 🔍
"""


def create_knowledge_base() -> LocalKnowledgeBase:
    """Factory function for knowledge base creation."""
    return LocalKnowledgeBase()

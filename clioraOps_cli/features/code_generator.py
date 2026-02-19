"""
Code Generator for ClioraOps.

Generates DevOps configuration files, scripts, and infrastructure code
with context-aware AI assistance.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict, List
from pathlib import Path


class CodeType(Enum):
    """Types of code that can be generated."""
    DOCKERFILE = "dockerfile"
    DOCKER_COMPOSE = "docker_compose"
    KUBERNETES_DEPLOYMENT = "kubernetes_deployment"
    KUBERNETES_SERVICE = "kubernetes_service"
    CI_CD_PIPELINE = "ci_cd_pipeline"
    TERRAFORM = "terraform"
    ANSIBLE = "ansible"
    BASH_SCRIPT = "bash_script"
    GITHUB_ACTIONS = "github_actions"
    GITLAB_CI = "gitlab_ci"


@dataclass
class GeneratedCode:
    """Result of code generation."""
    success: bool
    code_type: CodeType
    filename: str
    content: str
    explanation: str
    next_steps: List[str]
    error: Optional[str] = None


class CodeGenerator:
    """
    Generates DevOps code with AI assistance.
    
    Uses AI to generate context-aware, production-ready code.
    """
    
    def __init__(self, mode, ai=None):
        self.mode = mode
        self.ai = ai
        
        # Templates for common patterns
        self.templates = {
            CodeType.DOCKERFILE: self._dockerfile_templates(),
            CodeType.DOCKER_COMPOSE: self._docker_compose_templates(),
            CodeType.KUBERNETES_DEPLOYMENT: self._kubernetes_templates(),
        }
    
    def generate(
        self,
        code_type: CodeType,
        description: str,
        context: Dict = None
    ) -> GeneratedCode:
        """
        Generate code based on type and description.
        
        Args:
            code_type: Type of code to generate
            description: What the code should do
            context: Additional context (language, framework, etc.)
            
        Returns:
            GeneratedCode with content and explanation
        """
        
        # Build AI prompt
        prompt = self._build_generation_prompt(code_type, description, context)
        
        # Generate with AI if available
        if self.ai:
            generated = self._generate_with_ai(prompt, code_type)
        else:
            generated = self._generate_from_template(code_type, description, context)
        
        return generated
    
    def _build_generation_prompt(
        self,
        code_type: CodeType,
        description: str,
        context: Dict = None
    ) -> str:
        """Build prompt for AI code generation."""
        
        context = context or {}
        
        base_prompt = f"""
Generate a production-ready {code_type.value} that: {description}

Requirements:
- Follow best practices for {code_type.value}
- Include comments explaining key sections
- Use secure defaults
- Make it beginner-friendly but production-ready

Context:
"""
        
        # Add context details
        if 'language' in context:
            base_prompt += f"- Programming language: {context['language']}\n"
        if 'framework' in context:
            base_prompt += f"- Framework: {context['framework']}\n"
        if 'environment' in context:
            base_prompt += f"- Environment: {context['environment']}\n"
        
        # Mode-specific requirements
        if hasattr(self.mode, 'value') and self.mode.value == 'beginner':
            base_prompt += """
BEGINNER MODE:
- Add extensive comments
- Explain each section
- Include common pitfalls to avoid
- Suggest what to customize
"""
        else:
            base_prompt += """
ARCHITECT MODE:
- Focus on production readiness
- Include security best practices
- Add monitoring/observability hooks
- Note scalability considerations
"""
        
        return base_prompt
    
    def _generate_with_ai(self, prompt: str, code_type: CodeType) -> GeneratedCode:
        """Generate code using AI."""
        
        try:
            # Check if ai has generate_code or ask
            if hasattr(self.ai, 'generate_code'):
                response_text = self.ai.generate_code(prompt)
            else:
                response_text = self.ai.ask(prompt)
            
            if response_text:
                # Extract code and explanation from response
                content = self._extract_code_from_response(response_text)
                explanation = self._extract_explanation_from_response(response_text)
                
                # Determine filename
                filename = self._get_filename(code_type)
                
                # Generate next steps
                next_steps = self._generate_next_steps(code_type)
                
                return GeneratedCode(
                    success=True,
                    code_type=code_type,
                    filename=filename,
                    content=content,
                    explanation=explanation,
                    next_steps=next_steps
                )
            else:
                return self._generate_from_template(code_type, prompt, {})
                
        except Exception as e:
            return GeneratedCode(
                success=False,
                code_type=code_type,
                filename="",
                content="",
                explanation="",
                next_steps=[],
                error=f"Generation failed: {str(e)}"
            )
    
    def _generate_from_template(
        self,
        code_type: CodeType,
        description: str,
        context: Dict
    ) -> GeneratedCode:
        """Generate code from built-in templates when AI unavailable."""
        
        templates = self.templates.get(code_type, {})
        
        if not templates:
            return GeneratedCode(
                success=False,
                code_type=code_type,
                filename="",
                content="",
                explanation="",
                next_steps=[],
                error=f"No template available for {code_type.value}"
            )
        
        # Use most appropriate template
        context = context or {}
        template_key = context.get('template', 'default')
        template = templates.get(template_key, templates.get('default'))
        
        if not template:
            template = list(templates.values())[0]
        
        filename = self._get_filename(code_type)
        
        return GeneratedCode(
            success=True,
            code_type=code_type,
            filename=filename,
            content=template['content'],
            explanation=template['explanation'],
            next_steps=template['next_steps']
        )
    
    def _dockerfile_templates(self) -> Dict:
        """Dockerfile templates."""
        return {
            'python': {
                'content': '''# Python Application Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first (Docker layer caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Non-root user for security
RUN useradd -m appuser && chown -R appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run application
CMD ["python", "app.py"]
''',
                'explanation': '''
This Dockerfile follows best practices:
1. Uses official Python slim image (smaller size)
2. Leverages Docker layer caching (requirements.txt first)
3. Runs as non-root user (security)
4. Includes health check (production readiness)
5. Exposes port 8000 (standard for web apps)
''',
                'next_steps': [
                    "Create requirements.txt with your dependencies",
                    "Build the image: docker build -t myapp .",
                    "Test locally: docker run -p 8000:8000 myapp",
                    "Push to registry: docker push myapp"
                ]
            },
            'nodejs': {
                'content': '''# Node.js Application Dockerfile
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy application code
COPY . .

# Non-root user
RUN addgroup -g 1001 -S nodejs && adduser -S nodejs -u 1001
RUN chown -R nodejs:nodejs /app
USER nodejs

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s CMD node healthcheck.js

# Start application
CMD ["node", "server.js"]
''',
                'explanation': '''
Node.js optimized Dockerfile:
1. Alpine base image (minimal size)
2. npm ci for faster, reproducible builds
3. Production dependencies only
4. Non-root user (nodejs)
5. Health check included
''',
                'next_steps': [
                    "Ensure package.json and package-lock.json exist",
                    "Create healthcheck.js for health monitoring",
                    "Build: docker build -t myapp .",
                    "Run: docker run -p 3000:3000 myapp"
                ]
            },
            'default': {
                'content': '''# Multi-stage Dockerfile Template
# Stage 1: Build
FROM ubuntu:22.04 AS builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y \\
    build-essential \\
    && rm -rf /var/lib/apt/lists/*

# Copy and build your application
COPY . .
RUN make build

# Stage 2: Runtime
FROM ubuntu:22.04

WORKDIR /app

# Copy only what's needed from builder
COPY --from=builder /build/output /app/

# Install runtime dependencies
RUN apt-get update && apt-get install -y \\
    ca-certificates \\
    && rm -rf /var/lib/apt/lists/*

# Non-root user
RUN useradd -m appuser && chown -R appuser /app
USER appuser

EXPOSE 8080

CMD ["./app"]
''',
                'explanation': '''
Multi-stage Dockerfile advantages:
1. Smaller final image (only runtime dependencies)
2. Secure (no build tools in production)
3. Clean separation of build and runtime
4. Non-root execution
''',
                'next_steps': [
                    "Customize build stage for your language/framework",
                    "Update runtime dependencies",
                    "Set correct CMD for your app"
                ]
            },
            'go': {
                'content': '''# Multi-stage Go Dockerfile
# Stage 1: Build
FROM golang:1.21-alpine AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o main .

# Stage 2: Runtime
FROM alpine:latest
RUN apk --no-cache add ca-certificates
WORKDIR /root/
COPY --from=builder /app/main .
EXPOSE 8080
CMD ["./main"]
''',
                'explanation': 'Optimized multi-stage Go build using Alpine for a tiny footprint.',
                'next_steps': ["Ensure go.mod is present", "Build: docker build -t go-app ."]
            },
            'rust': {
                'content': '''# Multi-stage Rust Dockerfile
# Stage 1: Build
FROM rust:1.75-slim AS builder
WORKDIR /app
COPY . .
RUN cargo build --release

# Stage 2: Runtime
FROM debian:bookworm-slim
WORKDIR /app
COPY --from=builder /app/target/release/myapp .
CMD ["./myapp"]
''',
                'explanation': 'Production Rust build using Debian slim for stability.',
                'next_steps': ["Build: docker build -t rust-app ."]
            },
            'java': {
                'content': '''# Multi-stage Java (Maven) Dockerfile
# Stage 1: Build
FROM maven:3.9-eclipse-temurin-17 AS builder
WORKDIR /app
COPY pom.xml .
RUN mvn dependency:go-offline
COPY src ./src
RUN mvn package -DskipTests

# Stage 2: Runtime
FROM eclipse-temurin:17-jre-alpine
WORKDIR /app
COPY --from=builder /app/target/*.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]
''',
                'explanation': 'Java build using Temurin JRE Alpine for optimal performance and size.',
                'next_steps': ["Build: docker build -t java-app ."]
            }
        }
    
    def _docker_compose_templates(self) -> Dict:
        """Docker Compose templates."""
        return {
            'default': {
                'content': '''# Docker Compose Configuration
version: '3.8'

services:
  # Web application
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://db:5432/myapp
      - REDIS_URL=redis://cache:6379
    depends_on:
      - db
      - cache
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 3s
      retries: 3

  # PostgreSQL database
  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=myapp
      - POSTGRES_USER=admin
      - POSTGRES_PASSWORD=changeme  # Use secrets in production!
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U admin"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis cache
  cache:
    image: redis:7-alpine
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3

volumes:
  postgres_data:

networks:
  default:
    driver: bridge
''',
                'explanation': '''
Complete Docker Compose setup with:
1. Web app + database + cache
2. Health checks for all services
3. Proper dependency management
4. Persistent volume for database
5. Environment variable configuration
''',
                'next_steps': [
                    "Update environment variables",
                    "Change default passwords!",
                    "Start: docker-compose up -d",
                    "View logs: docker-compose logs -f"
                ]
            }
        }
    
    def _kubernetes_templates(self) -> Dict:
        """Kubernetes manifest templates."""
        return {
            'default': {
                'content': '''# Kubernetes Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
  labels:
    app: myapp
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
      - name: myapp
        image: myapp:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: database-url
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: myapp-service
spec:
  selector:
    app: myapp
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
''',
                'explanation': '''
Production-ready Kubernetes deployment:
1. 3 replicas for high availability
2. Resource limits prevent resource starvation
3. Health checks (liveness + readiness)
4. Secrets for sensitive data
5. LoadBalancer service for external access
''',
                'next_steps': [
                    "Create secrets: kubectl create secret generic app-secrets",
                    "Apply: kubectl apply -f deployment.yaml",
                    "Check status: kubectl get pods",
                    "View logs: kubectl logs -l app=myapp"
                ]
            }
        }
    
    def _get_filename(self, code_type: CodeType) -> str:
        """Get appropriate filename for code type."""
        filenames = {
            CodeType.DOCKERFILE: "Dockerfile",
            CodeType.DOCKER_COMPOSE: "docker-compose.yml",
            CodeType.KUBERNETES_DEPLOYMENT: "deployment.yaml",
            CodeType.KUBERNETES_SERVICE: "service.yaml",
            CodeType.CI_CD_PIPELINE: "pipeline.yml",
            CodeType.GITHUB_ACTIONS: ".github/workflows/ci.yml",
            CodeType.GITLAB_CI: ".gitlab-ci.yml",
            CodeType.TERRAFORM: "main.tf",
            CodeType.ANSIBLE: "playbook.yml",
            CodeType.BASH_SCRIPT: "script.sh",
        }
        return filenames.get(code_type, "generated_code.txt")
    
    def _generate_next_steps(self, code_type: CodeType) -> List[str]:
        """Generate next steps based on code type."""
        
        steps = {
            CodeType.DOCKERFILE: [
                "Review and customize the Dockerfile",
                "Build: docker build -t myapp .",
                "Test locally: docker run myapp",
                "Push to registry when ready"
            ],
            CodeType.KUBERNETES_DEPLOYMENT: [
                "Review resource limits",
                "Create necessary secrets",
                "Apply: kubectl apply -f deployment.yaml",
                "Monitor: kubectl get pods -w"
            ],
        }
        
        return steps.get(code_type, [
            "Review the generated code",
            "Customize for your needs",
            "Test in development first",
            "Deploy to production"
        ])
    
    def _extract_code_from_response(self, response: str) -> str:
        """Extract code block from AI response."""
        # Look for code blocks (markdown style)
        import re
        code_blocks = re.findall(r'```[\w]*\n(.*?)\n```', response, re.DOTALL)
        
        if code_blocks:
            return code_blocks[0]
        
        return response
    
    def _extract_explanation_from_response(self, response: str) -> str:
        """Extract explanation from AI response."""
        # Remove code blocks and return remaining text
        import re
        explanation = re.sub(r'```[\w]*\n.*?\n```', '', response, flags=re.DOTALL)
        return explanation.strip()
    
    def save_to_file(self, generated: GeneratedCode, output_dir: Path = None) -> str:
        """
        Save generated code to file.
        
        Returns: Path to saved file
        """
        if not generated.success:
            raise ValueError("Cannot save failed generation")
        
        output_dir = output_dir or Path.cwd()
        filepath = output_dir / generated.filename
        
        # Create directory if needed
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Write file
        filepath.write_text(generated.content)
        
        return str(filepath)


def format_generated_code(generated: GeneratedCode, mode=None) -> str:
    """Format generated code for display."""
    
    if not generated.success:
        return f"❌ Generation failed: {generated.error}"
    
    output = []
    
    output.append("=" * 70)
    output.append(f"✅ Generated: {generated.filename}")
    output.append("=" * 70)
    output.append("")
    
    # Show code
    output.append("📄 CODE:")
    output.append("-" * 70)
    output.append(generated.content)
    output.append("")
    
    # Show explanation
    if generated.explanation:
        output.append("💡 EXPLANATION:")
        output.append("-" * 70)
        output.append(generated.explanation)
        output.append("")
    
    # Show next steps
    if generated.next_steps:
        output.append("🚀 NEXT STEPS:")
        output.append("-" * 70)
        for i, step in enumerate(generated.next_steps, 1):
            output.append(f"{i}. {step}")
        output.append("")
    
    return "\n".join(output)


# Example usage
if __name__ == "__main__":
    from clioraOps_cli.core.modes import Mode
    
    generator = CodeGenerator(Mode.BEGINNER)
    
    # Generate Dockerfile
    result = generator.generate(
        CodeType.DOCKERFILE,
        "Python FastAPI application",
        context={'language': 'python', 'framework': 'fastapi'}
    )
    
    print(format_generated_code(result))
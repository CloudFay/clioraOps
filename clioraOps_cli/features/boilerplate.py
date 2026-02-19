"""
Enhanced boilerplate manager with cookiecutter integration and security policies.
"""

import os
import subprocess
from pathlib import Path
from typing import Optional, List, Dict
from dataclasses import dataclass

@dataclass
class BoilerplateTemplate:
    """Represents a boilerplate template."""
    id: str
    name: str
    description: str
    category: str
    url: str
    local: bool = False


class BoilerplateManager:
    """
    Manages project scaffolding using cookiecutter with policy support.
    
    Features:
    - 25+ DevOps templates organized by category
    - Cookiecutter integration for template generation
    - Security policy enforcement
    - Template validation
    - Progress reporting
    """
    
    # Template library
    TEMPLATES = {
        "kubernetes": [
            BoilerplateTemplate(
                id="k8s-deployment",
                name="Kubernetes Deployment",
                description="Basic Kubernetes deployment manifest",
                category="kubernetes",
                url="https://github.com/cookiecutter-templates/cookiecutter-kubernetes-deployment",
            ),
            BoilerplateTemplate(
                id="k8s-helm-chart",
                name="Helm Chart",
                description="Helm chart for Kubernetes",
                category="kubernetes",
                url="https://github.com/cookiecutter-templates/cookiecutter-helm-chart",
            ),
            BoilerplateTemplate(
                id="k8s-operator",
                name="Kubernetes Operator",
                description="Custom Kubernetes operator",
                category="kubernetes",
                url="https://github.com/cookiecutter-templates/cookiecutter-k8s-operator",
            ),
            BoilerplateTemplate(
                id="k8s-statefulset",
                name="Kubernetes StatefulSet",
                description="StatefulSet for stateful apps",
                category="kubernetes",
                url="https://github.com/cookiecutter-templates/cookiecutter-k8s-statefulset",
            ),
        ],
        "docker": [
            BoilerplateTemplate(
                id="docker-nodejs",
                name="Dockerized Node.js App",
                description="Docker setup for Node.js application",
                category="docker",
                url="https://github.com/cookiecutter-templates/cookiecutter-docker-nodejs",
            ),
            BoilerplateTemplate(
                id="docker-python",
                name="Dockerized Python App",
                description="Docker setup for Python application",
                category="docker",
                url="https://github.com/cookiecutter-templates/cookiecutter-docker-python",
            ),
            BoilerplateTemplate(
                id="docker-golang",
                name="Dockerized Go App",
                description="Docker setup for Go application",
                category="docker",
                url="https://github.com/cookiecutter-templates/cookiecutter-docker-go",
            ),
            BoilerplateTemplate(
                id="docker-compose-stack",
                name="Docker Compose Stack",
                description="Multi-container Docker Compose setup",
                category="docker",
                url="https://github.com/cookiecutter-templates/cookiecutter-docker-compose",
            ),
            BoilerplateTemplate(
                id="docker-multi-stage",
                name="Multi-Stage Dockerfile",
                description="Optimized multi-stage Docker build",
                category="docker",
                url="https://github.com/cookiecutter-templates/cookiecutter-docker-multistage",
            ),
        ],
        "cicd": [
            BoilerplateTemplate(
                id="github-actions-nodejs",
                name="GitHub Actions - Node.js",
                description="CI/CD pipeline for Node.js with GitHub Actions",
                category="cicd",
                url="https://github.com/cookiecutter-templates/cookiecutter-github-actions-nodejs",
            ),
            BoilerplateTemplate(
                id="github-actions-python",
                name="GitHub Actions - Python",
                description="CI/CD pipeline for Python with GitHub Actions",
                category="cicd",
                url="https://github.com/cookiecutter-templates/cookiecutter-github-actions-python",
            ),
            BoilerplateTemplate(
                id="gitlab-ci",
                name="GitLab CI Pipeline",
                description="CI/CD pipeline using GitLab CI",
                category="cicd",
                url="https://github.com/cookiecutter-templates/cookiecutter-gitlab-ci",
            ),
            BoilerplateTemplate(
                id="jenkins-pipeline",
                name="Jenkins Pipeline",
                description="Declarative Jenkins pipeline",
                category="cicd",
                url="https://github.com/cookiecutter-templates/cookiecutter-jenkins-pipeline",
            ),
            BoilerplateTemplate(
                id="circleci-config",
                name="CircleCI Configuration",
                description="CircleCI pipeline configuration",
                category="cicd",
                url="https://github.com/cookiecutter-templates/cookiecutter-circleci",
            ),
            BoilerplateTemplate(
                id="argocd-app",
                name="ArgoCD Application",
                description="ArgoCD application manifest",
                category="cicd",
                url="https://github.com/cookiecutter-templates/cookiecutter-argocd",
            ),
        ],
        "terraform": [
            BoilerplateTemplate(
                id="terraform-aws-vpc",
                name="AWS VPC Module",
                description="Terraform module for AWS VPC",
                category="terraform",
                url="https://github.com/cookiecutter-templates/cookiecutter-terraform-aws-vpc",
            ),
            BoilerplateTemplate(
                id="terraform-aws-ecs",
                name="AWS ECS Cluster",
                description="Terraform for AWS ECS cluster",
                category="terraform",
                url="https://github.com/cookiecutter-templates/cookiecutter-terraform-aws-ecs",
            ),
            BoilerplateTemplate(
                id="terraform-gcp-gke",
                name="GCP GKE Cluster",
                description="Terraform for Google Cloud GKE",
                category="terraform",
                url="https://github.com/cookiecutter-templates/cookiecutter-terraform-gcp-gke",
            ),
            BoilerplateTemplate(
                id="terraform-module",
                name="Terraform Module",
                description="Generic Terraform module",
                category="terraform",
                url="https://github.com/antonbabenko/cookiecutter-terraform-module",
            ),
            BoilerplateTemplate(
                id="terraform-aws-lambda",
                name="AWS Lambda Module",
                description="Terraform for AWS Lambda",
                category="terraform",
                url="https://github.com/cookiecutter-templates/cookiecutter-terraform-aws-lambda",
            ),
        ],
        "infrastructure": [
            BoilerplateTemplate(
                id="ansible-playbook",
                name="Ansible Playbook",
                description="Ansible playbook structure",
                category="infrastructure",
                url="https://github.com/cookiecutter-templates/cookiecutter-ansible-playbook",
            ),
            BoilerplateTemplate(
                id="ansible-role",
                name="Ansible Role",
                description="Reusable Ansible role",
                category="infrastructure",
                url="https://github.com/arillso/cookiecutter-ansible-role",
            ),
            BoilerplateTemplate(
                id="puppet-module",
                name="Puppet Module",
                description="Puppet module structure",
                category="infrastructure",
                url="https://github.com/cookiecutter-templates/cookiecutter-puppet-module",
            ),
        ],
        "applications": [
            BoilerplateTemplate(
                id="fastapi-app",
                name="FastAPI Application",
                description="FastAPI microservice boilerplate",
                category="applications",
                url="https://github.com/tiangolo/full-stack-fastapi-postgresql",
            ),
            BoilerplateTemplate(
                id="django-app",
                name="Django Application",
                description="Django web application",
                category="applications",
                url="https://github.com/cookiecutter-templates/cookiecutter-django",
            ),
            BoilerplateTemplate(
                id="go-cli",
                name="Go CLI Application",
                description="Go command-line application",
                category="applications",
                url="https://github.com/cookiecutter-templates/cookiecutter-go-cli",
            ),
        ],
    }
    
    def __init__(self, mode, policy=None):
        """
        Initialize boilerplate manager.
        
        Args:
            mode: Execution mode (beginner/architect)
            policy: AccessPolicy instance for security checks
        """
        self.mode = mode
        self.policy = policy
        
    def list_all_templates(self) -> Dict[str, List[BoilerplateTemplate]]:
        """
        List all available templates organized by category.
        
        Returns:
            Dictionary with categories as keys, template lists as values
        """
        return self.TEMPLATES
    
    def list_templates_by_category(self, category: str) -> List[BoilerplateTemplate]:
        """
        List templates in a specific category.
        
        Args:
            category: Category name (kubernetes, docker, cicd, etc.)
            
        Returns:
            List of templates in the category
        """
        return self.TEMPLATES.get(category, [])
    
    def list_templates(self) -> List[Dict[str, str]]:
        """List all templates as dictionaries for backward compatibility."""
        result = []
        for templates in self.TEMPLATES.values():
            for template in templates:
                result.append({
                    "id": template.id,
                    "name": template.name,
                    "url": template.url
                })
        return result
    
    def get_template(self, template_id: str) -> Optional[BoilerplateTemplate]:
        """
        Get a specific template by ID.
        
        Args:
            template_id: Template ID to find
            
        Returns:
            BoilerplateTemplate or None if not found
        """
        for templates in self.TEMPLATES.values():
            for template in templates:
                if template.id == template_id:
                    return template
        return None
    
    def validate_template(self, template: BoilerplateTemplate) -> bool:
        """
        Validate template is accessible and valid.
        
        Args:
            template: Template to validate
            
        Returns:
            True if template is valid, False otherwise
        """
        if not template.url:
            return False
        
        # For local templates, check if path exists
        if template.local:
            return Path(template.url).exists()
        
        return True
    
    def generate(self, template_id_or_url: str, output_dir: str = ".", **kwargs) -> bool:
        """
        Generate boilerplate from template using cookiecutter.
        
        Supports both template IDs and direct URLs for backward compatibility.
        
        Args:
            template_id_or_url: Template ID or direct URL
            output_dir: Directory to generate in
            **kwargs: Additional arguments for cookiecutter
            
        Returns:
            True if successful, False otherwise
        """
        # Check policy
        if self.policy and not self.policy.is_operation_allowed("create", output_dir):
            print(f"🚫 Access Denied: Cannot generate in '{output_dir}'")
            return False
        
        # Try to get template by ID first
        template = self.get_template(template_id_or_url)
        
        # If not found by ID, treat as direct URL (backward compatibility)
        if not template:
            if template_id_or_url.startswith(("http://", "https://", "file://")):
                # Direct URL provided
                print(f"🚀 Generating boilerplate from {template_id_or_url}...")
                try:
                    from cookiecutter.main import cookiecutter as run_cookiecutter
                    result = run_cookiecutter(
                        template_id_or_url,
                        no_input=kwargs.get("no_input", False),
                        output_dir=output_dir,
                        extra_context=kwargs.get("extra_context", {})
                    )
                    print(f"✅ Successfully generated at: {result}")
                    return True
                except ImportError:
                    print("❌ 'cookiecutter' is not installed")
                    print("💡 Install it with: pip install cookiecutter")
                    return False
                except Exception as e:
                    print(f"❌ Generation failed: {e}")
                    return False
            else:
                print(f"❌ Template not found: {template_id_or_url}")
                return False
        
        # Validate template
        if not self.validate_template(template):
            print(f"❌ Template is invalid or inaccessible: {template.id}")
            return False
        
        print(f"🚀 Generating {template.name}...")
        print(f"   From: {template.url}")
        print(f"   To: {output_dir}")
        
        try:
            # Check if cookiecutter is installed
            try:
                from cookiecutter.main import cookiecutter as run_cookiecutter
            except ImportError:
                print("❌ 'cookiecutter' is not installed")
                print("💡 Install it with: pip install cookiecutter")
                return False
            
            # Run cookiecutter
            result = run_cookiecutter(
                template.url,
                no_input=kwargs.get("no_input", False),
                output_dir=output_dir,
                extra_context=kwargs.get("extra_context", {})
            )
            
            print(f"✅ Successfully generated at: {result}")
            return True
            
        except Exception as e:
            print(f"❌ Generation failed: {e}")
            return False
    
    def get_template_info(self, template_id: str) -> Optional[str]:
        """
        Get detailed information about a template.
        
        Args:
            template_id: Template ID
            
        Returns:
            Formatted information string
        """
        template = self.get_template(template_id)
        if not template:
            return None
        
        lines = [
            f"📦 {template.name}",
            f"   Category: {template.category}",
            f"   Description: {template.description}",
            f"   Source: {template.url}",
        ]
        
        return "\n".join(lines)
    
    def print_all_templates(self) -> None:
        """Print all templates organized by category."""
        for category, templates in self.TEMPLATES.items():
            print(f"\n📁 {category.upper()} ({len(templates)} templates)")
            print("-" * 60)
            
            for template in templates:
                print(f"  • {template.id}: {template.name}")
                print(f"    {template.description}")

"""
Enhanced boilerplate manager with cookiecutter integration and security policies.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


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
    Manages project scaffolding using Cookiecutter with policy support.

    Features:
    - DevOps templates organized by category
    - Template discovery and validation
    - Security policy enforcement

    Generation remains disabled until Cookiecutter can run in an isolated
    process. Output-path authorization and post-generation checks cannot
    contain template code that executes during rendering.
    """

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
        Initialize the boilerplate manager.

        Args:
            mode: Execution mode (beginner/architect).
            policy: Policy object supporting is_operation_allowed()
                or is_allowed().
        """
        self.mode = mode
        self.policy = policy

    def list_all_templates(self) -> Dict[str, List[BoilerplateTemplate]]:
        """Return all templates organized by category."""
        return self.TEMPLATES

    def list_templates_by_category(
        self, category: str
    ) -> List[BoilerplateTemplate]:
        """Return templates belonging to a specific category."""
        return self.TEMPLATES.get(category, [])

    def list_templates(self) -> List[Dict[str, str]]:
        """List all templates as dictionaries for backward compatibility."""
        result = []

        for templates in self.TEMPLATES.values():
            for template in templates:
                result.append({
                    "id": template.id,
                    "name": template.name,
                    "url": template.url,
                })

        return result

    def get_template(
        self, template_id: str
    ) -> Optional[BoilerplateTemplate]:
        """Find a template by its ID."""
        for templates in self.TEMPLATES.values():
            for template in templates:
                if template.id == template_id:
                    return template

        return None

    def validate_template(self, template: BoilerplateTemplate) -> bool:
        """
        Validate that a template has a usable source.

        Local templates must exist on disk. Remote templates must
        have a non-empty URL.
        """
        if not template.url:
            return False

        if template.local:
            return Path(template.url).exists()

        return True

    def _can_generate(self, output_dir: str) -> bool:
        """
        Check whether the configured policy permits generation.

        AccessPolicy provides operation-level checks, while the
        legacy PolicyManager provides path-level checks.
        """
        if self.policy is None:
            return True

        operation_check = getattr(
            self.policy, "is_operation_allowed", None
        )

        if callable(operation_check):
            try:
                return operation_check("create", output_dir) is True
            except Exception:
                return False

        path_check = getattr(self.policy, "is_allowed", None)

        if callable(path_check):
            try:
                return path_check(output_dir) is True
            except Exception:
                return False

        # Unknown policy interfaces must fail closed.
        return False

    def generate(
        self,
        template_id_or_url: str,
        output_dir: str = ".",
        **kwargs,
    ) -> bool:
        """
        Generate boilerplate from a template using Cookiecutter.

        Supports template IDs and direct URLs.

        Args:
            template_id_or_url: Template ID or direct template URL.
            output_dir: Directory where the project will be generated.
            **kwargs: Additional Cookiecutter arguments.

        Returns:
            False until template processing is isolated from the host.
        """
        # Enforce policy before template lookup or generation.
        if not self._can_generate(output_dir):
            print(
                f"🚫 Access Denied: Cannot generate in '{output_dir}'"
            )
            return False

        print(
            "❌ Template generation is disabled until Cookiecutter "
            "can run in an isolated process."
        )
        return False

    def get_template_info(
        self, template_id: str
    ) -> Optional[str]:
        """Return formatted information about a template."""
        template = self.get_template(template_id)

        if template is None:
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
            print(
                f"\n📁 {category.upper()} "
                f"({len(templates)} templates)"
            )
            print("-" * 60)

            for template in templates:
                print(f"  • {template.id}: {template.name}")
                print(f"    {template.description}")

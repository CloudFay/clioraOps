# ClioraOps Deployment Guide

**Version:** 0.3.1
**Last Updated:** October 26, 2026

This guide covers local development, Docker-based deployment, the optional web interface, standalone packaging, and remote development. Verify platform-specific instructions against the current repository before deploying.

---

## Table of Contents

1. [Overview](#overview)
2. [Deployment Methods](#deployment-methods)
3. [Configuration](#configuration)
4. [AI Provider Setup](#ai-provider-setup)
5. [Troubleshooting](#troubleshooting)
6. [Production Checklist](#production-checklist)
7. [Advanced Topics](#advanced-topics)
8. [Support and Resources](#support-and-resources)

---

## Overview

ClioraOps supports several deployment approaches. The appropriate option depends on your workflow, required features, and security requirements.

| Environment | Best For | Complexity | Requirements |
|---|---|---|---|
| Local Python CLI | Development, testing, and learning | Low | Python and project dependencies |
| Docker | Reproducible environments and isolation | Moderate | Docker and a validated image configuration |
| Web interface | Browser-based demonstrations | Moderate | Optional web dependencies |
| Standalone binary | Portable distribution | Moderate | A supported and tested build process |
| Dev Container | Remote development and onboarding | Moderate | VS Code or a compatible development platform |

**Dependency installation options**

Install the core CLI without requesting the optional Gradio dependency:

```bash
python -m pip install -e .
```

Install the CLI with the web interface dependencies:

```
Temporarily unavailable: The Gradio web interface is paused while we resolve compatibility with a secure Pillow release. Do not install Gradio separately as a workaround. The core CLI remains available.
```

Run these commands from the repository root. The `web` extra is defined in `setup.py`.

---

## Deployment Methods

### 1. Local Python Development

**When to use:** Development, testing, debugging, and local learning.

#### Installation

Clone the repository and create a virtual environment:

```bash
git clone https://github.com/CloudFay/clioraOps.git
cd clioraOps

python -m venv .venv
```

Activate the environment.

Linux/macOS:

```bash
source .venv/bin/activate
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install ClioraOps:

```bash
python -m pip install -e .
```

If the repository's interactive AI setup script is available, run:

```bash
python scripts/setup_ai.py
```

Start the CLI:

```bash
clioraops start
```

Check the project's declared Python requirement before selecting an interpreter.

#### Configuration

ClioraOps uses `~/.clioraops/config.json` as its default configuration path, according to the existing project documentation.

An example configuration is:

```json
{
  "ai_provider": "gemini",
  "ai_api_key": "",
  "mode": "beginner",
  "nl_generation_enabled": true,
  "nl_auto_execute": false,
  "shell": "/bin/bash"
}
```

Treat this as an illustrative example. Verify supported configuration keys against the current implementation.

Avoid committing API keys or other secrets to source control. Prefer environment variables or an appropriate secrets-management mechanism where supported.

#### Advantages

- Direct access to the installed CLI features.
- Easy debugging and customization.
- No container runtime required.
- Suitable for learning and local development.

#### Limitations

- Requires a compatible Python environment.
- Dependencies must be maintained.
- AI-powered functionality may require provider credentials or a locally running model.

---

### 2. Docker Deployment

**When to use:** Reproducible environments, container-based workflows, and isolation from the host's Python environment.

Before starting, inspect the repository's `Dockerfile` and Compose configuration. The commands below apply only if the corresponding files and services are configured.

#### Build an image

From the repository root:

```bash
docker build -t clioraops .
```

Run the image using the entrypoint and command supported by that image. For example, if it supports the `clioraops start` command:

```bash
docker run -it \
  -e GEMINI_API_KEY="$GEMINI_API_KEY" \
  clioraops start
```

Add a persistent configuration mount only after confirming the correct host and container paths. For example, if the application uses `/root/.clioraops` inside the container:

```bash
docker run -it \
  -v "$HOME/.clioraops:/root/.clioraops" \
  -e GEMINI_API_KEY="$GEMINI_API_KEY" \
  clioraops start
```

#### Docker Compose

If a suitable `compose.yaml` or `docker-compose.yml` exists, start its configured services using:

```bash
docker compose up -d
docker compose ps
```

The exact services and configuration depend on the repository's Compose file. Do not assume that an Ollama service or a web-interface service is included unless it is explicitly configured.

If the Compose configuration references provider credentials, define the required variables using a local environment file or your deployment platform's secrets mechanism. Do not commit real credentials.

To inspect logs:

```bash
docker compose logs
```

To enter a running service, replace `clioraops` with the actual service name:

```bash
docker compose exec clioraops sh
```

Use `bash` instead of `sh` only if the container includes Bash.

#### Advantages

- Reproducible dependency environments.
- Separation from the host's Python installation.
- Integration with container-based development and CI/CD.
- Easier environment consistency across machines.

#### Limitations

- Requires Docker.
- Volume mounts and file permissions need attention.
- Container networking and secrets must be configured correctly.
- Containers alone do not guarantee production security, availability, or isolation from every host-level risk.

For additional instructions, see [DOCKER_SETUP_GUIDE.md](./DOCKER_SETUP_GUIDE.md), if present in the repository.

---

### 3. Web Interface (Gradio)

**When to use:** Browser-based demonstrations and interactive use through a web interface.

The web interface is an optional installation. Gradio is not requested by the standard core installation.

#### Installation

From the repository root, activate the project's virtual environment and run:

```
Temporarily unavailable: The Gradio web interface is paused while we resolve compatibility with a secure Pillow release. Do not install Gradio separately as a workaround. The core CLI remains available.
```

This installs the project together with the dependency declared under the `web` extra in `setup.py`.

If you only need the CLI, use the standard installation instead:

```bash
python -m pip install -e .
```

#### Start the web interface

Run:

```bash
python clioraOps_cli/web_interface.py
```

Open the local address reported by the application. The documented default is:

`http://localhost:7860`

If the application reports a different address or port, use the address shown in its output.

#### Documented interface features

The existing web-interface documentation describes:

- Beginner and Architect modes.
- A chat interface with mode awareness.
- Built-in command examples.
- Response streaming.

Confirm the behavior against the current implementation before relying on any feature in a production workflow.

#### Docker deployment

If the Docker image includes the optional web dependencies and the application supports this launch command, a service may follow this pattern:

```yaml
services:
  clioraops-web:
    build: .
    ports:
      - "127.0.0.1:7860:7860"
    environment:
      GEMINI_API_KEY: ${GEMINI_API_KEY}
    command: python clioraOps_cli/web_interface.py
```

This is an example, not a verified replacement for the repository's actual Compose configuration. Confirm the working directory, installed extras, launch command, and port before using it.

Binding the published port to `127.0.0.1` restricts direct access through the host's network interfaces. If remote access is needed, configure suitable authentication and access controls before exposing the service.

#### Advantages

- Browser-based interaction.
- Useful for demonstrations and users who prefer a graphical interface.
- Avoids requiring users to interact directly with the CLI.

#### Limitations

- Requires the optional web dependencies.
- May not expose every CLI capability.
- Remote access introduces additional security considerations.
- Performance and concurrency depend on the application implementation and deployment configuration.

For additional details, see [WEB_INTERFACE_GUIDE.md](./WEB_INTERFACE_GUIDE.md).

**Dependency security:** The optional web extra introduces additional dependencies. Review compatibility and security advisories for these packages separately from the core CLI dependencies. Making Gradio optional reduces the default installation footprint; it does not itself resolve vulnerabilities in Gradio's dependency tree.

---

### 4. Standalone Binary

**When to use:** Portable distribution where users should not have to manage Python directly.

The repository must contain a supported build process before the following steps can be used.

#### Build

If `scripts/build_executable.py` exists and supports your environment, install the required packaging tool:

```bash
python -m pip install PyInstaller
```

Then run:

```bash
python scripts/build_executable.py
```

Check the build output for the generated executable's location and filename.

#### Usage

Use the executable path and command supported by the generated artifact. For example, if the build produces a compatible CLI executable under `dist/`:

```bash
./dist/clioraops --help
```

On Windows, use the generated `.exe` filename if applicable.

#### Advantages

- Can simplify distribution.
- May reduce the need for users to install Python separately.
- Can package application dependencies.

#### Limitations

- Builds are generally platform-specific.
- Native libraries and provider integrations may require additional packaging.
- Binary creation and execution must be tested on each supported target platform.

Do not distribute an executable until its build process and essential workflows have been validated.

---

### 5. Dev Container and Remote Development

**When to use:** Consistent development environments, VS Code Remote Containers, or GitHub Codespaces.

#### Setup

1. Install VS Code and the Dev Containers extension.
2. Clone the ClioraOps repository.
3. Open the repository in VS Code.
4. Use **Reopen in Container** if a valid Dev Container configuration exists in the repository.

Alternatively, create a Codespace if GitHub Codespaces is enabled for the repository and your account.

The configuration in `.devcontainer/devcontainer.json`, if present, is the source of truth for the actual development environment.

#### Install dependencies

For a core CLI development environment:

```bash
python -m pip install -e .
```

If your development work requires the web interface:

```
Temporarily unavailable: The Gradio web interface is paused while we resolve compatibility with a secure Pillow release. Do not install Gradio separately as a workaround. The core CLI remains available.
```

Run tests using the project's configured test suite:

```bash
python -m pytest -q
```

#### Advantages

- More consistent development environments.
- Easier onboarding and collaboration.
- Reduced dependence on a developer's host configuration.

#### Limitations

- Requires a compatible development platform.
- Setup may need internet access.
- Resource limits and availability depend on the selected platform.

---

## Configuration

### Configuration file

The existing documentation identifies `~/.clioraops/config.json` as the default configuration file.

An illustrative configuration is:

```json
{
  "ai_provider": "gemini",
  "ai_api_key": "",
  "mode": "beginner",
  "nl_generation_enabled": true,
  "nl_auto_execute": false,
  "nl_show_alternatives": false,
  "shell": "/bin/bash",
  "theme": "dark",
  "verbose": false
}
```

The available options and defaults may vary by version. Confirm them against the current configuration implementation.

### AI provider settings

| Setting | Purpose |
|---|---|
| `ai_provider` | Selects the configured AI provider, where supported. |
| `ai_api_key` | Stores a provider credential if the implementation supports this setting. |
| `ai_model` | Selects a model if model selection is implemented. |

The project documentation describes integrations for Gemini, OpenAI, Anthropic, and Ollama. Availability depends on the installed dependencies, provider configuration, and current implementation.

### Natural-language settings

| Setting | Purpose |
|---|---|
| `nl_generation_enabled` | Controls natural-language command generation if supported. |
| `nl_auto_execute` | Controls the configured automatic-execution behavior if supported. |
| `nl_show_alternatives` | Controls the display of alternative suggestions if supported. |

Review command execution, authorization, and approval behavior before enabling automatic execution. Do not assume that a configuration setting bypasses or overrides execution policies.

### Environment variables

Provider integrations may use environment variables such as:

```bash
export GEMINI_API_KEY="your-key"
export OPENAI_API_KEY="your-key"
export ANTHROPIC_API_KEY="your-key"
```

Set only the variables supported by the selected provider integration.

Do not assume that variables such as `CLIORAOPS_MODE`, `CLIORAOPS_SHELL`, or `NL_AUTO_EXECUTE` are recognized unless the current implementation reads them.

For local development, a `.env` file can be used only if the application loads it:

```dotenv
GEMINI_API_KEY=your-key
```

Keep files containing credentials out of source control. Use your deployment platform's secrets mechanism for shared or production environments.

---

## AI Provider Setup

### Gemini

1. Create an API key through [Google AI Studio](https://aistudio.google.com/app/apikey).
2. Set `GEMINI_API_KEY` in your environment.
3. Start ClioraOps and verify that the provider is available.

Example for Bash-compatible shells:

```bash
export GEMINI_API_KEY="your-key"
clioraops start
```

Provider limits, model availability, and pricing can change. Consult the provider's current documentation.

### OpenAI

1. Create an API key through the [OpenAI platform](https://platform.openai.com/api-keys).
2. Set `OPENAI_API_KEY`.
3. Verify that the integration is available in your installed version.

```bash
export OPENAI_API_KEY="your-key"
clioraops start
```

### Anthropic

1. Create an API key through the [Anthropic Console](https://console.anthropic.com/).
2. Set `ANTHROPIC_API_KEY`.
3. Verify that the integration is available in your installed version.

```bash
export ANTHROPIC_API_KEY="your-key"
clioraops start
```

### Ollama

1. Install Ollama from [ollama.com](https://ollama.com/download).
2. Download a model supported by your local environment.
3. Start the Ollama service.
4. Configure ClioraOps to use the local provider, if supported by your installation.

Example Ollama commands:

```bash
ollama pull mistral
ollama serve
```

Run the service in the appropriate terminal or service manager for your environment. Local inference avoids sending prompts to a hosted model provider, but resource requirements depend on the model and hardware.

See [OLLAMA_SETUP.md](./OLLAMA_SETUP.md), if present, for additional project-specific instructions.

---

## Troubleshooting

### Python version or installation errors

Check the active interpreter:

```bash
python --version
```

If the version is unsupported, create a virtual environment using a compatible interpreter and reinstall the project:

```bash
python -m venv .venv
```

Activate the environment, then run:

```bash
python -m pip install -e .
python -m pip check
```

### Gradio or web-interface import errors

If the web interface reports that Gradio is missing, activate the correct virtual environment and install the optional extra from the repository root:

```
Temporarily unavailable: The Gradio web interface is paused while we resolve compatibility with a secure Pillow release. Do not install Gradio separately as a workaround. The core CLI remains available.
```

Confirm that the environment's Python interpreter is the one used to run the web interface.

### AI provider unavailable

If an AI provider cannot be found or initialized:

1. Verify that the integration is available in the installed version.
2. Confirm that the correct environment variable is set.
3. Check that the credential is valid.
4. Verify network access for hosted providers.
5. If using Ollama, confirm that the service is running and the selected model is installed.

### Docker cannot connect to its daemon

1. Confirm Docker is installed and running.
2. Check the active Docker context.
3. Verify the permissions required by your operating system.
4. Inspect the relevant container logs.

Follow the official Docker documentation for platform-specific permission guidance. Docker access can grant powerful control over the host, so do not change permissions without understanding the consequences.

### Configuration file problems

If the configuration file cannot be read:

1. Verify the expected path.
2. Validate the JSON syntax.
3. Check filesystem permissions.
4. Back up the file before modifying or resetting it.
5. Confirm that its keys match the current configuration implementation.

Validate JSON syntax with:

```bash
python -m json.tool path/to/config.json
```

Replace the example path with the actual location of the file.

### Natural-language functionality unavailable

If natural-language features are not working:

1. Confirm the feature is enabled, if configurable.
2. Verify that a supported provider is configured.
3. Check provider credentials and connectivity.
4. Inspect the application output for errors.
5. Try a simpler request to distinguish provider failures from intent-classification problems.

Do not enable automatic command execution simply to troubleshoot command generation.

### Verification commands

Run these from the repository root and within the intended virtual environment:

```bash
python --version
python -m pip show clioraops
python -m pip check
clioraops --help
python -m pytest -q
```

The repository's current CLI implementation and tests are the source of truth for available commands and supported behavior.

---

## Production Checklist

Review this checklist before using ClioraOps beyond local development.

### Installation and testing

- [ ] Use a supported Python version or a validated container image.
- [ ] Install only the dependency extras required for the deployment.
- [ ] Confirm that the application starts successfully.
- [ ] Run the relevant test suite.
- [ ] Check dependency compatibility and known vulnerabilities.
- [ ] Confirm that the selected release or commit is intended for deployment.

### Configuration

- [ ] Configure the required AI provider.
- [ ] Keep credentials outside source control.
- [ ] Verify supported configuration options.
- [ ] Review natural-language command-generation and execution settings.
- [ ] Confirm shell and user preferences where applicable.
- [ ] Back up persistent configuration when appropriate.

### Security

- [ ] Use an appropriate secrets-management mechanism.
- [ ] Restrict access to configuration files and directories.
- [ ] Review command execution, authorization, sandboxing, and approval behavior.
- [ ] Do not expose the web interface publicly without suitable access controls.
- [ ] Limit container privileges, network exposure, and mounted paths.
- [ ] Review dependency advisories, including optional dependencies.
- [ ] Confirm that logs do not disclose credentials or sensitive information.

### Operations

- [ ] Document startup, shutdown, and recovery procedures.
- [ ] Understand the selected AI provider's limits and costs.
- [ ] Establish a dependency-update process.
- [ ] Test behavior when providers or external services are unavailable.
- [ ] Document the deployment configuration and required environment variables without secret values.

---

## Advanced Topics

### Custom AI models

If the selected provider integration supports custom model selection, configure the model through the supported configuration mechanism.

Example configuration pattern:

```json
{
  "ai_provider": "openai",
  "ai_model": "your-supported-model",
  "ai_api_key": ""
}
```

Confirm the supported model identifier with the provider and the current ClioraOps implementation. Keep credentials out of committed configuration files.

### Multi-user deployments

Before sharing an installation between users, determine whether ClioraOps supports the required session, configuration, credential, and filesystem isolation.

Do not assume that a custom configuration-directory variable or shared configuration path is supported unless the current implementation provides it. Use separate credentials and appropriate access controls where necessary.

### Kubernetes deployment

A Kubernetes deployment may use ConfigMaps for non-sensitive configuration and Secrets for credentials. The following commands illustrate the general approach; they do not constitute a complete deployment.

Create a ConfigMap from a validated configuration file:

```bash
kubectl create configmap clioraops-config \
  --from-file=config.json
```

Create a Secret from an environment variable:

```bash
kubectl create secret generic clioraops-keys \
  --from-literal=gemini-api-key="$GEMINI_API_KEY"
```

Before deploying, prepare and review the required Kubernetes manifests. Validate the image, entrypoint, environment-variable mapping, resource limits, security context, networking, health checks, and secret access. Apply only manifests that have been tested for your environment.

### CI/CD integration

ClioraOps can be installed and tested in a CI/CD workflow using the commands supported by the project.

Example GitHub Actions workflow pattern:

```yaml
steps:
  - name: Check out repository
    uses: actions/checkout@v4

  - name: Set up Python
    uses: actions/setup-python@v5
    with:
      python-version: "3.13"

  - name: Install ClioraOps
    run: python -m pip install -e .

  - name: Check dependency consistency
    run: python -m pip check

  - name: Run tests
    run: python -m pytest -q
```

Adapt this example to the repository's actual CI configuration and supported Python versions. Do not assume additional CLI commands exist unless verified against the installed application.

---

## Support and Resources

- **Documentation:** [docs/](../docs/)
- **Issues:** [GitHub Issues](https://github.com/CloudFay/clioraOps/issues)
- **Setup guide:** [SETUP.md](../SETUP.md), if present
- **Contributing:** [CONTRIBUTING.md](../CONTRIBUTING.md), if present
- **Web interface guide:** [WEB_INTERFACE_GUIDE.md](./WEB_INTERFACE_GUIDE.md)
- **Docker setup guide:** [DOCKER_SETUP_GUIDE.md](./DOCKER_SETUP_GUIDE.md), if present
- **Ollama setup:** [OLLAMA_SETUP.md](./OLLAMA_SETUP.md), if present

---

**Version:** 0.3.1
**Last Updated:** October 26, 2026
**Status:** Deployment guide. Verify platform-specific instructions and security requirements against the current repository before production use.

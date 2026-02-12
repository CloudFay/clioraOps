# Getting Started with ClioraOps

## Prerequisites

Before running ClioraOps, ensure you have the following installed:

1.  **Python 3.10+**:
    ```bash
    python3 --version
    ```
2.  **GitHub CLI (`gh`)**:
    -   **Linux**: `sudo apt install gh` (or use package manager)
    -   **macOS**: `brew install gh`
    -   **Windows**: `winget install GitHub.cli`
3.  **GitHub Copilot Extension**:
    ```bash
    gh extension install github/gh-copilot
    gh auth login
    ```

## Installation

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/your-repo/clioraOps.git
    cd clioraOps
    ```

2.  **Install dependencies**:
    ```bash
    pip install -e .
    ```

## Running ClioraOps

Start an interactive session:
```bash
clioraops start
```

### Modes

Upon starting, you can choose between two modes:

*   **Beginner**: Focuses on learning fundamentals, using analogies, and providing safe defaults. It proactively warns about potentially dangerous commands.
*   **Architect**: Focuses on advanced concepts, production readiness, trade-offs, and assumes a higher level of technical knowledge.

You can switch modes at any time within the session using `switch to [mode]`.

## Basic Usage

Once in the interactive shell (`clioraops>`), you can run commands directly:

### 1. Try a Command Safely
Check if a command is safe before running it.
```bash
try rm -rf /            # WARNING: Dangerous operation detected!
try kubectl delete pod  # CAUTION: Resource deletion.
try docker ps           # SAFE: List running containers (read-only)
```

### 2. Explain Concepts
Get a detailed explanation tailored to your current mode.
```bash
explain kubernetes services
explain what is dependency injection
```

### 3. Generate Code
Create boilerplate code for common DevOps tasks.
```bash
generate dockerfile python fastapi
generate k8s deployment nginx replicas=3
generate ci github-actions verify-test-deploy
```

### 4. Debug Errors
Paste an error message to get an analysis and potential fix.
```bash
debug connection refused to localhost:8080
debug permission denied /var/run/docker.sock
```

### 5. Review Scripts
Analyze a script file for security issues and bad practices.
```bash
review ./deploy.sh
```

### 6. Visualize Architecture
Generate an ASCII diagram of a system architecture.
```bash
design microservices
design kubernetes
design cicd
```

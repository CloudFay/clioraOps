# ClioraOps Web Interface (Gradio)

**Version:** 0.3.1  
**Status:** Experimental

The web interface provides a browser-based alternative to the CLI, making ClioraOps accessible without terminal access.

---

## Overview

The Gradio-powered web interface allows you to interact with ClioraOps through a modern, user-friendly UI instead of the terminal. Perfect for:

- **Demonstrations**: Show ClioraOps to teams without requiring terminal knowledge
- **Accessibility**: Enable users who prefer graphical interfaces
- **Testing**: Validate responses in a controlled web environment
- **Sharing**: Host on a server for team access

---

## Quick Start

### 1. Launch the Web Interface

```bash
# Clone and setup
cd clioraOps
python3 -m venv venv && source venv/bin/activate
pip install -e .

# Run the web interface
python clioraOps_cli/web_interface.py
```

Expected output:
```
Running on local URL:  http://0.0.0.0:7860
```

### 2. Access the Interface

Open your browser:
```
http://localhost:7860
```

---

## Features

### Mode Selection
Switch between **Beginner** and **Architect** modes directly in the UI:
- **Beginner**: Analogies, simple explanations, safety warnings
- **Architect**: Technical depth, production patterns, trade-offs

### Chat Interface
- Ask questions naturally (e.g., "What is Kubernetes?")
- Generate commands (e.g., "show me running containers")
- Built-in examples for quick exploration

### Built-in Examples
Quick-start prompts:
- `try docker ps` - Execute explicit commands
- `design microservices` - Create architecture diagrams
- `what is Kubernetes?` - Get explanations
- `explain CI/CD` - Learn DevOps concepts

---

## Configuration

The web interface respects the same configuration as the CLI:

```bash
# Environment variables
export GEMINI_API_KEY="your-key"
python clioraOps_cli/web_interface.py

# Or with multiple providers
export GEMINI_API_KEY="..."
export OPENAI_API_KEY="..."
python clioraOps_cli/web_interface.py
```

---

## Deployment Options

### Local Development

```bash
python clioraOps_cli/web_interface.py
# Accessible at http://localhost:7860 (local only)
```

### Remote Server (Single User)

```bash
python clioraOps_cli/web_interface.py --server_name 0.0.0.0
# Accessible at http://<server-ip>:7860
```

### Docker Deployment

Add to your `docker-compose.yml`:

```yaml
services:
  clioraops-web:
    build: .
    ports:
      - "7860:7860"
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
    command: python clioraOps_cli/web_interface.py
```

Start:
```bash
docker-compose up clioraops-web
```

### Public Sharing (Temporary)

```python
# In web_interface.py, modify launch call:
web.launch(share=True)  # Creates public URL
```

---

## Usage Examples

### Example 1: Ask a Question

1. Select **Beginner** mode
2. Type: "What are microservices?"
3. Click **Send**
4. View AI-powered explanation

### Example 2: Generate a Command

1. Select **Beginner** mode
2. Type: "show me all running docker containers"
3. Click **Send**
4. ClioraOps generates: `docker ps -a`
5. Review and copy the command

### Example 3: Switch Modes

1. Select **Architect** mode
2. Type: "explain Kubernetes architecture"
3. Receive more technical, detailed response
4. Use for production design discussions

---

## Troubleshooting

### Port 7860 Already in Use

```bash
# Kill existing process
lsof -i :7860 | awk 'NR!=1 {print $2}' | xargs kill -9

# Or specify a different port
# (Modify web_interface.py line 84: server_port=7861)
```

### AI Provider Not Available

```bash
# Verify environment variables
echo $GEMINI_API_KEY

# Or set them:
export GEMINI_API_KEY="your-key"
python clioraOps_cli/web_interface.py
```

### Gradio Not Installed

```bash
pip install -e .  # Includes gradio>=4.0.0
```

---

## Security Considerations

### For Local Use
✅ Safe to use on localhost

### For Remote/Team Deployment
⚠️ **Important**: 
- Never expose without authentication
- Don't share public URLs in production
- Keep API keys in environment variables only
- Consider adding:
  - Reverse proxy with auth (nginx, Caddy)
  - Rate limiting
  - HTTPS/SSL

Example with reverse proxy (nginx):

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /path/to/cert;
    ssl_certificate_key /path/to/key;

    location / {
        auth_basic "ClioraOps";
        auth_basic_user_file /etc/nginx/.htpasswd;
        
        proxy_pass http://127.0.0.1:7860;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## Limitations

- Gradio interface is single-threaded (one user at a time recommended)
- For multi-user access, consider Docker + load balancing
- Command execution is captured via stdout redirection (some edge cases may differ from CLI)

---

## Advanced: Custom Configuration

Edit `web_interface.py` to customize:

```python
# Change port
def launch(self, share=False):
    interface = self.create_interface()
    interface.launch(
        server_name="0.0.0.0",
        server_port=7861,  # Change here
        share=share
    )

# Add custom styling
with gr.Blocks(theme=gr.themes.Soft()) as interface:
    # ... rest of interface

# Enable authentication
interface.launch(
    auth=[("user", "password")],  # Simple auth
)
```

---

## Comparison: CLI vs Web Interface

| Feature | CLI | Web |
|---------|-----|-----|
| **Speed** | ⚡⚡⚡ Fast | ⚡⚡ Moderate |
| **Accessibility** | Terminal required | Browser only |
| **Multi-user** | No | Limited (single thread) |
| **Scripting** | ✅ Yes | ❌ No |
| **Mobile Access** | ❌ No | ✅ Yes |
| **Remote Access** | ❌ SSH required | ✅ HTTP/S |

---

## Next Steps

- Run `python clioraOps_cli/web_interface.py` to start
- Visit examples in the interface
- For production, see [Deployment Guide](./DEPLOYMENT_GUIDE.md)

---

**Need help?** Open an issue on [GitHub](https://github.com/CloudFay/clioraOps/issues)

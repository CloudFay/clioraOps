import os
from datetime import datetime

DOCS_PATH = os.path.join(os.path.dirname(__file__), "../../docs")
LEARNING_LOG = os.path.join(DOCS_PATH, "learning_log.md")

def log_learning_session(topic, mode, user_input, ai_output, visual_output="", review_output=""):
    os.makedirs(DOCS_PATH, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"""
## {timestamp} | Topic: {topic} | Mode: {mode}

**User Input:**  
{user_input}

**AI Output:**  
{ai_output}

**Visualizer Output:**  
{visual_output}

**Reviewer Output:**  
{review_output}

---
"""

    with open(LEARNING_LOG, "a") as f:
        f.write(entry)

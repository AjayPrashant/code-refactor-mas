# ollama_client.py
# Safe Ollama client wrapper 🚀

import os
import ollama

# Set correct Ollama URL
# → Inside Docker Compose → http://ollama:11434
# → Locally → http://localhost:11434
os.environ["OLLAMA_BASE_URL"] = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")

# Simple wrapper for consistent usage
def chat_with_ollama(model, messages):
    return ollama.chat(
        model=model,
        messages=messages
    )

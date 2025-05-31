# Code Refactor MAS 🚀

A multi-agent system that automatically analyzes, refactors, reviews, and generates unit tests for code — powered by:

✅ LangGraph 0.4.7  
✅ Ollama + Local CodeLlama 7B  
✅ Rich CLI  
✅ Stateful Memory (StateGraph)  

---

## How to run locally

1️⃣ Start Ollama:

```bash
ollama serve
ollama pull codellama:7b
```

2️⃣ Install dependencies:

```bash 
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2️⃣ Run MAS:

```bash
python updated_main_with_rich.py
```
# agents/analyzer_agent.py

import ollama
from ollama_client import chat_with_ollama

def analyzer_agent(state: dict) -> dict:
    code_input = state["latest_code"]  # ✅ Extract from state

    prompt = f"Analyze this {state.get('language', 'Python')} code and describe any issues or bad practices:\n\n{code_input}"

    response = chat_with_ollama(
        model='codellama:7b',
        messages=[
            {'role': 'user', 'content': prompt}
        ]
    )
    analysis = response['message']['content']

    print("=== ANALYSIS ===")
    print(analysis)

    # Update state
    state["analysis"] = analysis
    state.setdefault("history", []).append({"agent": "Analyzer", "output": analysis})

    return state


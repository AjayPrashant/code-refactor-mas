# agents/refactor_agent.py

import ollama
from ollama_client import chat_with_ollama

def refactor_agent(state: dict) -> dict:
    analysis = state["analysis"]

    prompt = f"""
You are a code refactoring expert.

Based on the following analysis, refactor the code to improve it.
Provide the entire improved version of the code.

--- Analysis ---
{analysis}

# Refactored Code:
    """

    response = chat_with_ollama(
        model='codellama:7b',
        messages=[
            {'role': 'user', 'content': prompt}
        ]
    )

    refactored_code = response['message']['content']

    print("=== REFACTORED CODE ===")
    print(refactored_code)

    # Update state
    state["refactored_code"] = refactored_code
    state.setdefault("history", []).append({"agent": "Refactor", "output": refactored_code})

    return state

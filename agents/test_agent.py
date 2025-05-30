# agents/test_agent.py

import ollama
from ollama_client import chat_with_ollama

def test_agent(state: dict) -> dict:
    refactored_code = state["refactored_code"]

    prompt = f"""
You are an expert test engineer.

Generate {state.get('language', 'Python')} unit tests for the following code.
Use the unittest or pytest framework.

--- Refactored Code ---
{refactored_code}

# Unit Tests:
    """

    response = chat_with_ollama(
        model='codellama:7b',
        messages=[
            {'role': 'user', 'content': prompt}
        ]
    )

    tests = response['message']['content']

    print("=== UNIT TESTS ===")
    print(tests)

    # Update state
    state["unit_tests"] = tests
    state.setdefault("history", []).append({"agent": "Test", "output": tests})

    return state

# agents/review_agent.py

import ollama
from ollama_client import chat_with_ollama

def review_agent(state: dict) -> dict:
    refactored_code = state["refactored_code"]

    prompt = f"""
You are a senior software engineer.

Please review the following refactored {state.get('language', 'Python')} code.
- Point out any remaining issues
- Suggest any further improvements
- If it's perfect, say "Code is ready."

--- Refactored Code ---
{refactored_code}

# Review Comments:
    """

    response = chat_with_ollama(
        model='codellama:7b',
        messages=[
            {'role': 'user', 'content': prompt}
        ]
    )

    review = response['message']['content']

    print("=== REVIEW ===")
    print(review)

    # Update state
    state["review"] = review
    state.setdefault("history", []).append({"agent": "Review", "output": review})

    return state

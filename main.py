# main.py

from langgraph.graph import END, Graph
import ollama
from agents.analyzer_agent import analyzer_agent
from agents.refactor_agent import refactor_agent
from agents.review_agent import review_agent

# Example input code (later: can take file input)
INPUT_CODE = """
def add(a,b):
  return a+b
"""

# Initialize Graph
graph = Graph()

# Add agents as nodes
graph.add_node("Analyzer", analyzer_agent)
graph.add_node("Refactor", refactor_agent)
graph.add_node("Review", review_agent)

# Define edges
graph.set_entry_point("Analyzer")
graph.add_edge("Analyzer", "Refactor")
graph.add_edge("Refactor", "Review")
graph.add_edge("Review", END)

# Compile graph
workflow = graph.compile()

# Run the MAS workflow
result = workflow.invoke(INPUT_CODE)
print("=== FINAL OUTPUT ===")
print(result)

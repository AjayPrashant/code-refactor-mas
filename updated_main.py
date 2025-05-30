# updated_main.py

import os
from langgraph.graph import END, Graph
from agents.analyzer_agent import analyzer_agent
from agents.refactor_agent import refactor_agent
from agents.review_agent import review_agent

# --- CONFIG ---
INPUT_FOLDER = "input_code"
OUTPUT_FOLDER = "output_code"

# Create output folder if it doesn't exist
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# --- Setup LangGraph Graph ---
graph = Graph()
graph.add_node("Analyzer", analyzer_agent)
graph.add_node("Refactor", refactor_agent)
graph.add_node("Review", review_agent)

graph.set_entry_point("Analyzer")
graph.add_edge("Analyzer", "Refactor")
graph.add_edge("Refactor", "Review")
graph.add_edge("Review", END)

workflow = graph.compile()

# --- Process each .py file ---
for filename in os.listdir(INPUT_FOLDER):
    if filename.endswith(".py"):
        file_path = os.path.join(INPUT_FOLDER, filename)
        print(f"\n=== Processing: {filename} ===")

        with open(file_path, "r") as f:
            input_code = f.read()

        result = workflow.invoke(input_code)

        # Save refactored file
        output_filename = filename.replace(".py", "_refactored.py")
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)

        with open(output_path, "w") as f:
            f.write(result)

        print(f"✅ Saved refactored file: {output_path}")

print("\n🎉 All files processed!")

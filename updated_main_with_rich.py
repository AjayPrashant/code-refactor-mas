# updated_main_with_rich.py
# Uses LangGraph StateGraph with memory
# Adds Rich CLI for nice display 🚀

import os
from langgraph.graph import END, StateGraph
from agents.analyzer_agent import analyzer_agent
from agents.refactor_agent import refactor_agent
from agents.review_agent import review_agent
from agents.test_agent import test_agent

from rich.console import Console
from rich.progress import track
from rich.panel import Panel

# --- CONFIG ---
INPUT_FOLDER = "input_code"
OUTPUT_FOLDER = "output_code"

# Setup Rich console
console = Console()

# --- Setup LangGraph StateGraph ---
graph = StateGraph(state_schema=dict)

# Add agents
graph.add_node("Analyzer", analyzer_agent)
graph.add_node("Refactor", refactor_agent)
graph.add_node("Review", review_agent)
graph.add_node("Test", test_agent)

# Define flow
graph.set_entry_point("Analyzer")
graph.add_edge("Analyzer", "Refactor")
graph.add_edge("Refactor", "Review")
graph.add_edge("Review", "Test")
graph.add_edge("Test", END)

# Compile workflow
workflow = graph.compile()

# --- Process .py files ---
py_files = [f for f in os.listdir(INPUT_FOLDER) if f.endswith(".py")]

if not py_files:
    console.print("[bold red]No .py files found in input_code/[/bold red]")
else:
    console.print(Panel("[bold cyan]🚀 Starting Code Refactor MAS with Memory[/bold cyan]", expand=False))

    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    for filename in track(py_files, description="Processing files..."):
        file_path = os.path.join(INPUT_FOLDER, filename)
        console.print(f"\n[bold yellow]📄 Processing: {filename}[/bold yellow]")

        # Read input code
        with open(file_path, "r") as f:
            input_code = f.read()

        # Initial state (memory)
        state = {
            "latest_code": input_code,
            "language": "Python",   # Optional → add auto-detect later!
            "history": []
        }

        # Run MAS workflow
        final_state = workflow.invoke(state)

        # Save refactored code
        output_filename = filename.replace(".py", "_refactored.py")
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)

        with open(output_path, "w") as f:
            f.write(final_state["refactored_code"])

        console.print(f"[green]✅ Saved refactored file: {output_path}[/green]")

        # Save unit tests (optional)
        tests_output_filename = filename.replace(".py", "_tests.py")
        tests_output_path = os.path.join(OUTPUT_FOLDER, tests_output_filename)

        with open(tests_output_path, "w") as f:
            f.write(final_state["unit_tests"])

        console.print(f"[green]✅ Saved unit tests: {tests_output_path}[/green]")

        # Optional: print full agent history
        console.print("\n[bold magenta]--- Agent History ---[/bold magenta]")
        for entry in final_state["history"]:
            console.print(f"[bold blue]{entry['agent']}[/bold blue]:\n{entry['output']}\n")

    console.print(Panel("[bold green]🎉 All files processed![/bold green]", expand=False))

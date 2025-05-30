# textual_mas.py
# Compatible with Textual 3.x (3.2.0)

import os
from langgraph.graph import END, Graph
from agents.analyzer_agent import analyzer_agent
from agents.refactor_agent import refactor_agent
from agents.review_agent import review_agent

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static
from textual.widgets.logging import LoggingView
from textual.widgets import Progress
from textual.reactive import var

# --- CONFIG ---
INPUT_FOLDER = "input_code"
OUTPUT_FOLDER = "output_code"

# Prepare LangGraph pipeline
graph = Graph()
graph.add_node("Analyzer", analyzer_agent)
graph.add_node("Refactor", refactor_agent)
graph.add_node("Review", review_agent)

graph.set_entry_point("Analyzer")
graph.add_edge("Analyzer", "Refactor")
graph.add_edge("Refactor", "Review")
graph.add_edge("Review", END)

workflow = graph.compile()

# --- Textual App ---
class MASApp(App):

    progress_value = var(0)

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield Static("🚀 Code Refactor MAS - Processing Files...", id="title")
        yield LoggingView(id="log")
        yield Progress(id="progress")

    def on_mount(self):
        # Get references to widgets
        self.log_view = self.query_one("#log", LoggingView)
        self.progress = self.query_one("#progress", Progress)

        # Start processing files
        self.process_files()

    def process_files(self):
        py_files = [f for f in os.listdir(INPUT_FOLDER) if f.endswith(".py")]

        if not py_files:
            self.log_view.write("[red]No .py files found in input_code/[/red]")
            return

        os.makedirs(OUTPUT_FOLDER, exist_ok=True)

        num_files = len(py_files)
        progress_step = 1 / num_files if num_files else 1

        for idx, filename in enumerate(py_files, 1):
            file_path = os.path.join(INPUT_FOLDER, filename)
            self.log_view.write(f"[yellow]📄 Processing: {filename}[/yellow]")

            with open(file_path, "r") as f:
                input_code = f.read()

            result = workflow.invoke(input_code)

            # Save output
            output_filename = filename.replace(".py", "_refactored.py")
            output_path = os.path.join(OUTPUT_FOLDER, output_filename)

            with open(output_path, "w") as f:
                f.write(result)

            self.log_view.write(f"[green]✅ Saved: {output_path}[/green]")

            # Update progress
            self.progress_value += progress_step
            self.progress.update(self.progress_value)

        self.log_view.write("[bold green]🎉 All files processed![/bold green]")
        self.progress.update(1.0)

if __name__ == "__main__":
    app = MASApp()
    app.run()

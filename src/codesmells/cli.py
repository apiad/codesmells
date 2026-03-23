import os
import hashlib
from pathlib import Path
from codesmells.storage import StorageManager
from codesmells.lexer import ProbabilisticLexer
from codesmells.alignment import FuzzyAlignmentEngine
from codesmells.models import Candidate, Binding

import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(help="CodeSmells: Agentic Architectural Refactoring Tool")
console = Console()

@app.command()
def scan(directory: str = "."):
    """Scan directory for anti-patterns."""
    console.print(f"Scanning [bold cyan]{directory}[/]...")
    
    storage = StorageManager()
    rules = storage.load_rules(str(storage.root_dir))
    if not rules:
        rules = storage.load_rules(directory)
        
    lexer = ProbabilisticLexer()
    engine = FuzzyAlignmentEngine()
    candidates = []

    for root, _, files in os.walk(directory):
        if ".codesmells" in root or ".git" in root or ".venv" in root:
            continue
        for file in files:
            if not file.endswith(".py"):
                continue
            
            file_path = Path(root) / file
            try:
                content = file_path.read_text()
            except UnicodeDecodeError:
                continue
                
            target_tokens = lexer.tokenize(content)
            
            for rule in rules:
                if any(pf not in content for pf in rule.pre_filters):
                    continue
                    
                for anti_pattern in rule.anti_patterns:
                    template_tokens = lexer.tokenize(anti_pattern)
                    score, bindings_dict = engine.align(target_tokens, template_tokens)
                    
                    if score >= rule.tau:
                        c_id = hashlib.md5(f"{rule.id}-{file_path}-{score}".encode()).hexdigest()[:8]
                        bindings = [
                            Binding(candidate_id=c_id, sigil=k, bound_value=v) 
                            for k, v in bindings_dict.items()
                        ] if bindings_dict else []
                        
                        candidate = Candidate(
                            id=c_id,
                            rule_id=rule.id,
                            file_path=str(file_path),
                            line_num=1,
                            raw_snippet=content[:500],
                            status="PENDING",
                            bindings=bindings
                        )
                        candidates.append(candidate)
                        break

    storage.save_candidates(candidates)

    table = Table(title="Pending Candidates")
    table.add_column("ID", style="dim")
    table.add_column("Rule", style="magenta")
    table.add_column("File", style="green")
    
    for c in candidates:
        table.add_row(c.id, c.rule_id, c.file_path)

    console.print(table)
    console.print("\n[bold]NEXT STEP:[/] inspect <id>")

@app.command()
def inspect(id: str):
    """Inspect a candidate and its bindings."""
    console.print(f"Inspecting candidate [bold cyan]{id}[/]...")
    # TODO: Implementation

@app.command()
def suggest(id: str):
    """Generate refactoring suggestion for a candidate."""
    console.print(f"Generating suggestion for [bold cyan]{id}[/]...")
    # TODO: Implementation

@app.command()
def ignore(id: str, template: str = typer.Option(..., help="Template to add to Safe patterns")):
    """Mark a candidate as safe."""
    console.print(f"Ignoring candidate [bold cyan]{id}[/] with template...")
    # TODO: Implementation

if __name__ == "__main__":
    app()

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
from rich.syntax import Syntax
from rich.panel import Panel

app = typer.Typer(help="CodeSmells: Agentic Architectural Refactoring Tool")
console = Console()

@app.command()
def scan(directory: str = typer.Argument(".", help="Directory to scan")):
    """Scan directory for anti-patterns."""
    console.print(f"Scanning [bold cyan]{directory}[/]...")
    
    storage = StorageManager()
    
    # Try to load rules from the target directory's .codesmells folder first
    target_rules_dir = Path(directory) / ".codesmells"
    rules = storage.load_rules(str(target_rules_dir))
    
    # Fallback to the global/project .codesmells folder
    if not rules:
        rules = storage.load_rules(str(storage.root_dir))
        
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
                    score, bindings_dict, indices = engine.align(target_tokens, template_tokens)
                    
                    if score >= rule.tau:
                        c_id = hashlib.md5(f"{rule.id}-{file_path}-{score}".encode()).hexdigest()[:8]
                        bindings = [
                            Binding(candidate_id=c_id, sigil=k, bound_value=v) 
                            for k, v in bindings_dict.items()
                        ] if bindings_dict else []
                        
                        # Extract snippet around the match
                        if indices:
                            start_token_idx, end_token_idx = indices
                            start_line = target_tokens[start_token_idx].line_num
                            end_line = target_tokens[end_token_idx].line_num
                            
                            # Get content lines
                            content_lines = content.splitlines()
                            snippet_start = max(0, start_line - 5)
                            snippet_end = min(len(content_lines), end_line + 5)
                            snippet = "\n".join(content_lines[snippet_start:snippet_end])
                        else:
                            snippet = content[:500]
                            start_line = 1

                        candidate = Candidate(
                            id=c_id,
                            rule_id=rule.id,
                            file_path=str(file_path),
                            line_num=start_line,
                            raw_snippet=snippet,
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
    
    storage = StorageManager()
    candidates = storage.load_candidates()
    
    candidate = next((c for c in candidates if c.id == id), None)
    if not candidate:
        console.print(f"[bold red]Error:[/] Candidate [bold cyan]{id}[/] not found.")
        raise typer.Exit(code=1)
        
    rules = storage.load_rules(str(storage.root_dir))
    if not rules:
        # Try to find rules in the candidate's top-level directory
        first_dir = Path(candidate.file_path).parts[0]
        if Path(first_dir).is_dir():
            rules = storage.load_rules(str(Path(first_dir) / ".codesmells"))
        
    rule = next((r for r in rules if r.id == candidate.rule_id), None)
    
    console.print(f"\n[bold magenta]Rule:[/] {candidate.rule_id}")
    if rule:
        console.print(f"[dim]Tau: {rule.tau}[/dim]")
        if rule.description:
            console.print(f"\n[bold yellow]Description:[/]\n{rule.description}")
        
    console.print(f"\n[bold green]File:[/] {candidate.file_path}")
    
    console.print("\n[bold]Raw Snippet:[/]")
    syntax = Syntax(candidate.raw_snippet, "python", theme="monokai", line_numbers=True)
    console.print(Panel(syntax, expand=False))
    
    if candidate.bindings:
        console.print("\n[bold yellow]Bindings:[/]")
        binding_table = Table(show_header=True, header_style="bold yellow")
        binding_table.add_column("Sigil")
        binding_table.add_column("Bound Value")
        for b in candidate.bindings:
            binding_table.add_row(b.sigil, b.bound_value)
        console.print(binding_table)
    else:
        console.print("\n[dim]No bindings found.[/dim]")

@app.command()
def suggest(id: str):
    """Generate refactoring suggestion for a candidate."""
    console.print(f"Generating suggestion for [bold cyan]{id}[/]...")
    
    storage = StorageManager()
    candidates = storage.load_candidates()
    
    candidate = next((c for c in candidates if c.id == id), None)
    if not candidate:
        console.print(f"[bold red]Error:[/] Candidate [bold cyan]{id}[/] not found.")
        raise typer.Exit(code=1)
        
    rules = storage.load_rules(str(storage.root_dir))
    if not rules:
        # Try to find rules in the candidate's top-level directory
        first_dir = Path(candidate.file_path).parts[0]
        if Path(first_dir).is_dir():
            rules = storage.load_rules(str(Path(first_dir) / ".codesmells"))
        
    rule = next((r for r in rules if r.id == candidate.rule_id), None)
    
    if not rule:
        console.print(f"[bold red]Error:[/] Rule [bold cyan]{candidate.rule_id}[/] not found.")
        raise typer.Exit(code=1)
        
    if not rule.refactor_template:
        console.print(f"[bold red]Error:[/] Rule [bold cyan]{rule.id}[/] has no refactoring template.")
        raise typer.Exit(code=1)
        
    import re
    hydrated = rule.refactor_template
    # Sort by length descending to match longer sigils first ($DB_POOL before $DB)
    sorted_bindings = sorted(candidate.bindings, key=lambda b: len(b.sigil), reverse=True)
    for binding in sorted_bindings:
        # Escape sigil for regex (it starts with $)
        pattern = re.escape(binding.sigil) + r"\b"
        hydrated = re.sub(pattern, binding.bound_value, hydrated)
        
    if rule.refactor_explanation:
        console.print(f"\n[bold yellow]Explanation:[/]\n{rule.refactor_explanation}")

    console.print("\n[bold green]Suggested Refactoring:[/]")
    syntax = Syntax(hydrated, "python", theme="monokai", line_numbers=True)
    console.print(Panel(syntax, expand=False))

@app.command()
def ignore(id: str, template: str = typer.Option(..., help="Template to add to Safe patterns")):
    """Mark a candidate as safe."""
    console.print(f"Ignoring candidate [bold cyan]{id}[/] with template...")
    
    storage = StorageManager()
    candidates = storage.load_candidates()
    
    candidate = next((c for c in candidates if c.id == id), None)
    if not candidate:
        console.print(f"[bold red]Error:[/] Candidate [bold cyan]{id}[/] not found.")
        raise typer.Exit(code=1)
        
    rules = storage.load_rules(str(storage.root_dir))
    if not rules:
        # Try to find rules in the candidate's top-level directory
        first_dir = Path(candidate.file_path).parts[0]
        if Path(first_dir).is_dir():
            rules = storage.load_rules(str(Path(first_dir) / ".codesmells"))
        
    rule = next((r for r in rules if r.id == candidate.rule_id), None)
    
    if not rule:
        console.print(f"[bold red]Error:[/] Rule [bold cyan]{candidate.rule_id}[/] not found.")
        raise typer.Exit(code=1)

    lexer = ProbabilisticLexer()
    engine = FuzzyAlignmentEngine()
    
    template_tokens = lexer.tokenize(template)
    snippet_tokens = lexer.tokenize(candidate.raw_snippet)
    
    # Validation Gate 1: S(template, raw_snippet) > 0.7
    score, _, _ = engine.align(snippet_tokens, template_tokens)
    if score < 0.7:
        console.print(f"[bold red]Validation Failure (Gate 1):[/] Template similarity to snippet is [bold yellow]{score:.2f}[/] (Expected > 0.7)")
        raise typer.Exit(code=1)
        
    # Validation Gate 2: Template complexity (must contain $SIGIL or ...)
    if not any(token.value.startswith("$") or token.value == "..." for token in template_tokens):
        console.print(f"[bold red]Validation Failure (Gate 2):[/] Template must contain at least one [bold yellow]$SIGIL[/] or [bold yellow]...[/]")
        raise typer.Exit(code=1)
        
    # Validation Gate 3: S(template, anti_pattern) < 0.9
    for anti_pattern in rule.anti_patterns:
        ap_tokens = lexer.tokenize(anti_pattern)
        ap_score, _, _ = engine.align(ap_tokens, template_tokens)
        if ap_score > 0.9:
            console.print(f"[bold red]Validation Failure (Gate 3):[/] Template is too similar to an anti-pattern ([bold yellow]{ap_score:.2f}[/] > 0.9)")
            raise typer.Exit(code=1)

    # All gates passed
    try:
        storage.update_rule_safe_patterns(rule.id, template)
        storage.update_candidate_status(id, "IGNORED")
        console.print(f"[bold green]Success:[/] Candidate [bold cyan]{id}[/] marked as [bold]IGNORED[/] and template added to [bold]{rule.id}.smell.md[/]")
    except Exception as e:
        console.print(f"[bold red]Error:[/] Failed to update rule: {e}")
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()

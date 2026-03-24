import os
import hashlib
from pathlib import Path
from typing import List, Optional
from codesmells.storage import StorageManager
from codesmells.lexer import ProbabilisticLexer
from codesmells.alignment import FuzzyAlignmentEngine
from codesmells.models import Candidate, Binding

import typer
from rich.console import Console
from rich.table import Table
from rich.syntax import Syntax
from rich.panel import Panel

app = typer.Typer(
    help="CodeSmells: Agentic Architectural Refactoring Tool",
)
console = Console()

@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """CodeSmells: Agentic Architectural Refactoring Tool"""
    if ctx.invoked_subcommand is None:
        console.print(Panel.fit(
            "[bold cyan]CodeSmells[/] - Agentic Architectural Refactoring Tool",
            subtitle="v0.3.0"
        ))

        console.print("\n[bold]DESCRIPTION[/]")
        console.print("  CodeSmells uses fuzzy alignment and probabilistic lexing to detect")
        console.print("  architectural anti-patterns in your Python codebase and suggest")
        console.print("  refactorings based on expert rule templates.")

        console.print("\n[bold]CORE WORKFLOW[/]")
        console.print("  1. [bold cyan]init[/]          Initialize the .codesmells/ environment.")
        console.print("  2. [bold cyan]add[/]           Create a new rule template from boilerplate.")
        console.print("  3. [bold cyan]validate[/]      Verify rules against their test patterns.")
        console.print("  4. [bold cyan]scan[/]          Scan the codebase for detected smells.")
        console.print("  5. [bold cyan]status[/]        Review detected candidates in the current session.")
        console.print("  6. [bold cyan]inspect <id>[/]  Examine a specific candidate and its bindings.")
        console.print("  7. [bold cyan]suggest <id>[/]  Generate a refactored code suggestion.")
        console.print("  8. [bold cyan]accept <id>[/]   Mark a candidate as addressed.")
        console.print("  9. [bold cyan]ignore <id>[/]   Mark a candidate as safe (adds to Safe patterns).")
        console.print("  10. [bold cyan]finish[/]       Complete the session and clear state.")
        console.print("  11. [bold cyan]install-skill[/] Install SKILL.md for AI agents.")

        console.print("\n[bold yellow]NEXT STEPS[/]")
        codesmells_dir = Path(".codesmells")
        if not codesmells_dir.exists():
            console.print("  ➜ Start by running [bold green]codesmells init[/] to set up your project.")
        else:
            storage = StorageManager()
            rules = storage.load_rules(str(codesmells_dir))
            if not rules:
                console.print("  ➜ No rules found. Use [bold green]codesmells add <name> <description>[/] to create one.")
                return

            candidates = storage.load_candidates()
            if not candidates:
                console.print("  ➜ Run [bold green]codesmells scan[/] to find architectural smells.")
            else:
                pending = [c for c in candidates if c.status == "PENDING"]
                if pending:
                    console.print(f"  ➜ You have [bold yellow]{len(pending)}[/] pending candidates. Use [bold green]codesmells status[/] to review them.")
                else:
                    console.print("  ➜ All candidates addressed. Run [bold green]codesmells finish[/] to wrap up.")

        console.print("\n[dim]Use 'codesmells <command> --help' for more information on a specific command.[/dim]")

def print_next_steps(candidates: List[Candidate]):
    if not candidates:
        console.print("\n[bold green]✨ Project is clean![/] No architectural smells detected.")
        console.print("[dim]Try adding more rules or scanning a different directory.[/dim]")
        return

    pending = [c for c in candidates if c.status == "PENDING"]
    if pending:
        c = pending[0]
        console.print(f"\n[bold yellow]NEXT STEP:[/] inspect {c.id} OR suggest {c.id}")
        console.print(f"[dim]Then use 'accept {c.id}' if fixed or 'ignore {c.id}' if safe.[/dim]")
    else:
        console.print("\n[bold green]NEXT STEP:[/] finish")
        console.print("[dim]All candidates have been addressed.[/dim]")

def suggest_alternative_ids(invalid_id: str, candidates: List[Candidate]):
    """Suggests valid IDs when an invalid one is provided."""
    if not candidates:
        console.print("[dim]No active session or candidates found.[/dim]")
        return

    # Sort by simple string distance (or just show all if few)
    import difflib
    valid_ids = [c.id for c in candidates]
    matches = difflib.get_close_matches(invalid_id, valid_ids, n=3, cutoff=0.3)

    if matches:
        console.print(f"[bold yellow]Did you mean one of these?[/] {', '.join(f'[bold cyan]{m}[/]' for m in matches)}")
    else:
        console.print(f"[bold yellow]Available IDs:[/] {', '.join(f'[bold cyan]{c.id}[/]' for c in candidates[:10])}")

    console.print("\n[dim]Run 'codesmells status' to see the full list of candidates.[/dim]")

def _print_status_table(candidates: List[Candidate]):
    table = Table(title="CodeSmells Session Status")
    table.add_column("ID", style="dim")
    table.add_column("Rule", style="magenta")
    table.add_column("File", style="green")
    table.add_column("Status", style="bold")

    for c in candidates:
        status_style = "yellow" if c.status == "PENDING" else "green" if c.status == "ACCEPTED" else "blue"
        table.add_row(c.id, c.rule_id, c.file_path, f"[{status_style}]{c.status}[/]")

    console.print(table)

@app.command()
def init():
    """Initialize CodeSmells in the current directory."""
    codesmells_dir = Path(".codesmells")
    if codesmells_dir.exists():
        console.print("[bold red]Error:[/] .codesmells directory already exists.")
        raise typer.Exit(code=1)

    codesmells_dir.mkdir()
    gitignore_file = codesmells_dir / ".gitignore"
    gitignore_file.write_text("session.json\n")

    console.print(f"[bold green]Success:[/] Initialized CodeSmells in {codesmells_dir}/.")
    console.print("[bold yellow]Next Step:[/] Use [bold]codesmells add <name> <description>[/] to create your first rule template.")
    console.print("[dim]Example: codesmells add \"Catch All Exception\" \"Avoid using bare except: or except Exception:\"[/dim]")

@app.command()
def add(name: str, description: str):
    """Add a new rule template."""
    codesmells_dir = Path(".codesmells")
    if not codesmells_dir.exists():
        console.print("[bold red]Error:[/] .codesmells directory not found. Run [bold]init[/] first.")
        raise typer.Exit(code=1)

    # Convert name to kebab-case
    import re
    kebab_name = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')
    file_path = codesmells_dir / f"{kebab_name}.smell.md"

    if file_path.exists():
        console.print(f"[bold red]Error:[/] Rule [bold cyan]{kebab_name}[/] already exists.")
        raise typer.Exit(code=1)

    template = f"""---
tau: 0.4
pre_filters:
  - "relevant_keyword"
---
# {name}

{description}

### Anti-Pattern
<!-- Describe the code pattern to avoid -->
```python
# Insert anti-pattern code here
```

### Refactoring
<!-- Describe the improved version -->
```python
# Insert refactored code here
```

### Refactor Explanation
<!-- Why is this better? -->

### Safe
<!-- Optional: examples that look like the anti-pattern but are safe -->
```python
# Insert safe example here
```
"""
    file_path.write_text(template)

    # Create corresponding .test.md
    test_file_path = codesmells_dir / f"{kebab_name}.smell.test.md"
    test_template = f"""# Test: {name}

### Anti-Pattern
<!-- Snippets that MUST match -->
```python
# Insert code that should trigger the rule
```

### Safe
<!-- Snippets that MUST NOT match -->
```python
# Insert code that looks similar but is safe
```
"""
    test_file_path.write_text(test_template)

    console.print(f"[bold green]Success:[/] Created rule template at [bold cyan]{file_path}[/].")
    console.print(f"[bold green]Success:[/] Created test template at [bold cyan]{test_file_path}[/].")
    console.print(f"\n[bold yellow]Next Step:[/] Edit [bold]{file_path}[/] and [bold]{test_file_path}[/] then fill in the following sections:")
    console.print("  1. [magenta]pre_filters:[/] Add keywords that MUST be present for this rule to apply.")
    console.print("  2. [magenta]Anti-Pattern:[/] Add a Python code block of the code you want to catch.")
    console.print("  3. [magenta]Refactoring:[/] Add a Python code block of the ideal code.")
    console.print("  4. [magenta]Tests:[/] Add examples to the .test.md file and run [bold green]codesmells validate[/].")
    console.print("\n[dim]Then run [bold]codesmells scan[/] to see your rule in action![/dim]")

@app.command()
def install_skill(
    path: Optional[str] = typer.Argument(None, help="Path to install the SKILL.md file (e.g. .gemini/skills)"),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing SKILL.md file")
):
    """Install the CodeSmells SKILL.md for AI agents."""
    template_path = Path(__file__).parent / "templates" / "SKILL.md"
    if not template_path.exists():
        console.print("[bold red]Error:[/] SKILL.md template not found.")
        raise typer.Exit(code=1)

    if not path:
        console.print("[bold cyan]CodeSmells AI Agent Skill[/]")
        console.print("This command installs a [bold]SKILL.md[/] file that provides instructions")
        console.print("to AI agents (Gemini, Claude, etc.) on how to use CodeSmells effectively.")
        
        console.print("\n[bold]Suggested Installation Paths:[/]")
        console.print("  - [bold yellow]Gemini CLI:[/]  .gemini/skills/codesmells/")
        console.print("  - [bold yellow]Claude Code:[/] .claude/skills/codesmells/")
        
        console.print("\n[bold]Example Usage:[/]")
        console.print("  [green]codesmells install-skill .gemini/skills/[/]")
        return

    dest_dir = Path(path) / "codesmells"
    dest_file = dest_dir / "SKILL.md"

    if dest_file.exists() and not force:
        console.print(f"[bold red]Error:[/] Skill already exists at [bold cyan]{dest_file}[/]. Use [bold]--force[/] to overwrite.")
        raise typer.Exit(code=1)

    try:
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_file.write_text(template_path.read_text())
        console.print(f"[bold green]Success:[/] Installed CodeSmells skill to [bold cyan]{dest_file}[/].")
    except Exception as e:
        console.print(f"[bold red]Error:[/] Failed to install skill: {e}")
        raise typer.Exit(code=1)

@app.command()
def validate(path_or_id: Optional[str] = typer.Argument(None, help="Path to a directory of rules, a rule file, or a rule ID")):
    """Validate rule templates against their test patterns and auto-tune thresholds."""
    storage = StorageManager()
    
    if path_or_id and Path(path_or_id).is_dir():
        rules = storage.load_rules(path_or_id)
    elif path_or_id:
        # Validate specific rule or file
        path_obj = Path(path_or_id)
        if path_obj.exists() and path_obj.name.endswith(".smell.md"):
            rules = [storage._parse_rule_file(path_obj)]
        else:
            # Assume it's a rule ID
            try:
                # Try recursive search
                found = list(Path(".").glob(f"**/{path_or_id}.smell.md"))
                if not found:
                    # Try in .codesmells
                    rule_file = storage.root_dir / f"{path_or_id}.smell.md"
                    if not rule_file.exists():
                        console.print(f"[bold red]Error:[/] Rule [bold cyan]{path_or_id}[/] not found.")
                        raise typer.Exit(code=1)
                    rule_file = rule_file
                else:
                    rule_file = found[0]
                rules = [storage._parse_rule_file(rule_file)]
            except Exception as e:
                console.print(f"[bold red]Error:[/] Failed to load rule {path_or_id}: {e}")
                raise typer.Exit(code=1)
    else:
        # Validate all rules in .codesmells
        rules = storage.load_rules(str(storage.root_dir))
        
    if not rules:
        console.print("[yellow]No rules found to validate.[/]")
        return

    lexer = ProbabilisticLexer()
    engine = FuzzyAlignmentEngine()
    
    total_passed = 0
    total_failed = 0
    
    for rule in rules:
        test = storage.load_rule_test(rule.id)
        if not test:
            console.print(f"[yellow]Skipping {rule.id}:[/] No test file found ([dim]{rule.id}.smell.test.md[/dim])")
            continue
            
        console.print(f"Validating [bold cyan]{rule.id}[/]...")
        
        # 1. Collect Anti-Pattern scores
        anti_scores = []
        for i, ap in enumerate(test.anti_patterns):
            target_tokens = lexer.tokenize(ap)
            max_s = 0.0
            for rule_ap in rule.anti_patterns:
                template_tokens = lexer.tokenize(rule_ap)
                score, _, _ = engine.align(target_tokens, template_tokens)
                max_s = max(max_s, score)
            anti_scores.append(max_s)

        # 2. Collect Safe Pattern scores
        safe_scores = []
        for i, safe in enumerate(test.safe_patterns):
            target_tokens = lexer.tokenize(safe)
            max_s = 0.0
            for rule_ap in rule.anti_patterns:
                template_tokens = lexer.tokenize(rule_ap)
                score, _, _ = engine.align(target_tokens, template_tokens)
                max_s = max(max_s, score)
            safe_scores.append(max_s)

        # 3. Auto-tune Tau
        min_anti = min(anti_scores) if anti_scores else 1.0
        max_safe = max(safe_scores) if safe_scores else 0.0
        
        if min_anti > max_safe:
            # Success: we have clear separation
            margin = min_anti - max_safe
            new_tau = (min_anti + max_safe) / 2
            
            # Enforce a minimum margin of 0.05 for stability
            if margin < 0.05:
                console.print(f"  [yellow]⚠[/] Warning: Narrow margin ({margin:.2f}). Consider making patterns more distinct.")
            
            console.print(f"  [green]✓[/] [bold]Auto-tuned tau:[/] [cyan]{new_tau:.2f}[/] (margin: [dim]{margin:.2f}[/dim])")
            for i, s in enumerate(anti_scores):
                console.print(f"    - Anti-Pattern #{i+1}: [green]{s:.2f}[/]")
            for i, s in enumerate(safe_scores):
                console.print(f"    - Safe Pattern #{i+1}: [blue]{s:.2f}[/]")
                
            storage.update_rule_tau(rule.id, new_tau)
            total_passed += 1
        else:
            # Failure: overlapping scores
            console.print("  [red]✗[/] [bold]Failure:[/] Overlapping scores. Cannot distinguish between bad and good examples.")
            overlap_anti_idx = anti_scores.index(min_anti)
            overlap_safe_idx = safe_scores.index(max_safe)
            console.print(f"    - Lowest Anti-Pattern (#{overlap_anti_idx+1}): [red]{min_anti:.2f}[/]")
            console.print(f"    - Highest Safe Pattern (#{overlap_safe_idx+1}): [red]{max_safe:.2f}[/]")
            total_failed += 1

    console.print(f"\n[bold]Summary:[/] [green]{total_passed} passed[/], [red]{total_failed} failed[/]")
    
    if total_failed > 0:
        raise typer.Exit(code=1)
    
    if total_failed > 0:
        raise typer.Exit(code=1)

@app.command(name="list")
def list_rules(directory: str = typer.Argument(".", help="Directory to search for rules")):
    """List all available code smell rules and their descriptions."""
    storage = StorageManager()
    rules = storage.load_rules(directory)
    
    if not rules:
        console.print("[yellow]No rules found.[/]")
        return

    from rich.table import Table
    table = Table(title="Available Code Smells")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Anti", style="red", justify="right")
    table.add_column("Safe", style="green", justify="right")
    table.add_column("Description", style="white")

    for rule in rules:
        test = storage.load_rule_test(rule.id)
        anti_count = len(test.anti_patterns) if test else 0
        safe_count = len(test.safe_patterns) if test else 0
        
        # Get first line of description or a truncated version
        short_desc = rule.description.split(".")[0] + "." if rule.description else "No description provided."
        table.add_row(rule.id, str(anti_count), str(safe_count), short_desc)

    console.print(table)

@app.command()
def scan(directory: str = typer.Argument(".", help="Directory to scan")):
    """Scan directory for anti-patterns."""
    storage = StorageManager()
    existing = storage.load_candidates()
    if any(c.status == "PENDING" for c in existing):
        console.print("[bold red]Error:[/] A scan session is already in progress with PENDING candidates.")
        console.print("Use [bold]status[/] to see them, or [bold]finish[/] to clear the current session.")
        raise typer.Exit(code=1)

    console.print(f"Scanning [bold cyan]{directory}[/]...")

    # Try to load rules from the target directory's .codesmells folder first
    target_rules_dir = Path(directory) / ".codesmells"
    rules = storage.load_rules(str(target_rules_dir))

    # Fallback to the global/project .codesmells folder
    if not rules:
        rules = storage.load_rules(str(storage.root_dir))

    if not rules:
        console.print("[bold red]Error:[/] No rule templates found to scan with.")
        console.print("Use [bold green]codesmells add <name> <description>[/] to create your first rule.")
        raise typer.Exit(code=1)

    lexer = ProbabilisticLexer()

    engine = FuzzyAlignmentEngine()
    candidates = []

    for root, _, files in os.walk(directory):
        if any(ignore in root for ignore in [".codesmells", ".git", ".venv", "__pycache__", "node_modules"]):
            continue
        for file in files:
            # Skip hidden files and common non-code extensions
            if file.startswith(".") or any(file.endswith(ext) for ext in [".pyc", ".lock", ".json", ".md"]):
                continue

            file_path = Path(root) / file
            try:
                # Basic check for text file
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read(1024 * 1024) # 1MB limit for safety
            except (UnicodeDecodeError, PermissionError):
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
    _print_status_table(candidates)
    print_next_steps(candidates)

@app.command()
def status():
    """Show the status of the current scan session."""
    storage = StorageManager()
    candidates = storage.load_candidates()
    if not candidates:
        console.print("[dim]No active session. Use [bold]scan[/] to start one.[/dim]")
        return

    _print_status_table(candidates)
    print_next_steps(candidates)

@app.command()
def accept(id: str):
    """Mark a candidate as solved/accepted."""
    storage = StorageManager()
    candidates = storage.load_candidates()

    candidate = next((c for c in candidates if c.id == id), None)
    if not candidate:
        console.print(f"[bold red]Error:[/] Candidate [bold cyan]{id}[/] not found.")
        suggest_alternative_ids(id, candidates)
        raise typer.Exit(code=1)

    storage.update_candidate_status(id, "ACCEPTED")
    console.print(f"[bold green]Accepted:[/] Candidate [bold cyan]{id}[/] marked as [bold]ACCEPTED[/].")

    # Reload and show remaining
    updated = storage.load_candidates()
    print_next_steps(updated)

@app.command()
def finish():
    """Finalize the session, print a report, and clear state."""
    storage = StorageManager()
    candidates = storage.load_candidates()
    if not candidates:
        console.print("[dim]No active session to finish.[/dim]")
        return

    console.print("[bold cyan]Finalizing Session Report...[/]\n")

    accepted = [c for c in candidates if c.status == "ACCEPTED"]
    ignored = [c for c in candidates if c.status == "IGNORED"]
    pending = [c for c in candidates if c.status == "PENDING"]

    console.print(f"✅ [bold green]Accepted:[/] {len(accepted)}")
    console.print(f"🙈 [bold blue]Ignored: [/] {len(ignored)}")
    if pending:
        console.print(f"⏳ [bold yellow]Pending: [/] {len(pending)}")

    storage.clear_session()
    console.print("\n[bold green]Session cleared.[/] Ready for a new [bold]scan[/].")

@app.command()
def inspect(id: str):
    """Inspect a candidate and its bindings."""
    console.print(f"Inspecting candidate [bold cyan]{id}[/]...")

    storage = StorageManager()
    candidates = storage.load_candidates()

    candidate = next((c for c in candidates if c.id == id), None)
    if not candidate:
        console.print(f"[bold red]Error:[/] Candidate [bold cyan]{id}[/] not found.")
        suggest_alternative_ids(id, candidates)
        raise typer.Exit(code=1)

    rules = storage.load_rules(str(storage.root_dir))

    # Also look in the directory where the candidate's file is
    candidate_file_path = Path(candidate.file_path)
    # Search for .codesmells in any parent of the candidate file up to the current dir
    curr = candidate_file_path.parent
    while curr != Path(".") and curr != Path("/"):
        if (curr / ".codesmells").is_dir():
            rules.extend(storage.load_rules(str(curr / ".codesmells")))
        if curr == curr.parent:
            break
        curr = curr.parent

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

    print_next_steps(candidates)

@app.command()
def suggest(id: str):
    """Generate refactoring suggestion for a candidate."""
    console.print(f"Generating suggestion for [bold cyan]{id}[/]...")

    storage = StorageManager()
    candidates = storage.load_candidates()

    candidate = next((c for c in candidates if c.id == id), None)
    if not candidate:
        console.print(f"[bold red]Error:[/] Candidate [bold cyan]{id}[/] not found.")
        suggest_alternative_ids(id, candidates)
        raise typer.Exit(code=1)

    rules = storage.load_rules(str(storage.root_dir))

    # Also look in the directory where the candidate's file is
    candidate_file_path = Path(candidate.file_path)
    # Search for .codesmells in any parent of the candidate file up to the current dir
    curr = candidate_file_path.parent
    while curr != Path(".") and curr != Path("/"):
        if (curr / ".codesmells").is_dir():
            rules.extend(storage.load_rules(str(curr / ".codesmells")))
        if curr == curr.parent:
            break
        curr = curr.parent

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

    print_next_steps(candidates)

@app.command()
def ignore(id: str, template: str = typer.Option(..., help="Template to add to Safe patterns")):
    """Mark a candidate as safe."""
    console.print(f"Ignoring candidate [bold cyan]{id}[/] with template...")

    storage = StorageManager()
    candidates = storage.load_candidates()

    candidate = next((c for c in candidates if c.id == id), None)
    if not candidate:
        console.print(f"[bold red]Error:[/] Candidate [bold cyan]{id}[/] not found.")
        suggest_alternative_ids(id, candidates)
        raise typer.Exit(code=1)

    rules = storage.load_rules(str(storage.root_dir))

    # Also look in the directory where the candidate's file is
    candidate_file_path = Path(candidate.file_path)
    # Search for .codesmells in any parent of the candidate file up to the current dir
    curr = candidate_file_path.parent
    while curr != Path(".") and curr != Path("/"):
        if (curr / ".codesmells").is_dir():
            rules.extend(storage.load_rules(str(curr / ".codesmells")))
        if curr == curr.parent:
            break
        curr = curr.parent

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
        console.print("[bold red]Validation Failure (Gate 2):[/] Template must contain at least one [bold yellow]$SIGIL[/] or [bold yellow]...[/]")
        raise typer.Exit(code=1)

    # Validation Gate 3: S(template, anti_pattern) < 0.95
    for anti_pattern in rule.anti_patterns:
        anti_tokens = lexer.tokenize(anti_pattern)
        score, _, _ = engine.align(template_tokens, anti_tokens)
        if score > 0.95:
            console.print(f"[bold red]Validation Failure (Gate 3):[/] Template is too similar to an anti-pattern (score: [bold yellow]{score:.2f}[/])")
            raise typer.Exit(code=1)


    # All gates passed
    try:
        storage.update_rule_safe_patterns(rule.id, template)
        storage.update_candidate_status(id, "IGNORED")
        console.print(f"[bold green]Success:[/] Candidate [bold cyan]{id}[/] marked as [bold]IGNORED[/] and template added to [bold]{rule.id}.smell.md[/]")

        # Reload and show remaining
        updated = storage.load_candidates()
        print_next_steps(updated)
    except Exception as e:
        console.print(f"[bold red]Error:[/] Failed to update rule: {e}")
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()

import re
import sys
import yaml
import importlib.resources
from pathlib import Path
from codesmells.types import Rule


class RuleParseError(Exception):
    pass


_CODE_BLOCK = re.compile(r"```(?:\w+)?\n(.*?)\n```", re.DOTALL)


_LANG_BY_EXT = {
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".jsx": "javascript",
    ".go": "go",
    ".rs": "rust",
    ".java": "java",
    ".rb": "ruby",
    ".md": "markdown",
}


def parse_rule_file(path: Path) -> Rule:
    """Parse a .smell.md file into a Rule. Raises RuleParseError on malformed input."""
    text = Path(path).read_text()
    frontmatter, body = _split_frontmatter(text)
    if not frontmatter.get("id"):
        raise RuleParseError(f"{path}: missing required field 'id'")

    anti = _extract_code_blocks(body, "### Anti-Pattern")
    if not anti:
        raise RuleParseError(f"{path}: missing required section '### Anti-Pattern' with code block")
    safe = _extract_code_blocks(body, "### Safe")
    refactor = _extract_code_blocks(body, "### Refactoring")

    return Rule(
        id=str(frontmatter["id"]),
        lang=list(frontmatter.get("lang", [])),
        tau=float(frontmatter.get("tau", 0.4)),
        severity=str(frontmatter.get("severity", "warn")),
        description=_extract_description(body),
        pre_filters=list(frontmatter.get("pre_filters", [])),
        anti_patterns=anti,
        safe_patterns=safe,
        refactor_template=refactor[0] if refactor else None,
        refactor_explanation=_extract_explanation(body, "### Refactoring"),
        source_path=str(path),
    )


def _split_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    try:
        fm = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError as e:
        raise RuleParseError(f"invalid YAML frontmatter: {e}") from e
    return fm, parts[2]


def _section(body: str, header: str) -> str:
    parts = body.split(header, 1)
    if len(parts) < 2:
        return ""
    rest = parts[1]
    nxt = re.search(r"\n#{1,3} ", rest)
    return rest[:nxt.start()] if nxt else rest


def _extract_code_blocks(body: str, header: str) -> list[str]:
    section = _section(body, header)
    return [m.group(1).strip() for m in _CODE_BLOCK.finditer(section)]


def _extract_description(body: str) -> str:
    nxt = re.search(r"\n### ", body)
    head = body[:nxt.start()] if nxt else body
    head = re.sub(r"^#\s+.*\n", "", head, flags=re.MULTILINE)
    return head.strip()


def _extract_explanation(body: str, header: str) -> str:
    section = _section(body, header)
    return _CODE_BLOCK.sub("", section).strip()


def load_rules_from_dir(dir_path: Path) -> list[Rule]:
    """Load every *.smell.md from dir_path. Warn on malformed; skip them."""
    rules = []
    for p in sorted(Path(dir_path).glob("*.smell.md")):
        try:
            rules.append(parse_rule_file(p))
        except RuleParseError as e:
            print(f"warn: rule {p.name}: {e}", file=sys.stderr)
    return rules


def detect_languages(root: Path) -> set[str]:
    """Walk root, return set of language tags inferred from file extensions."""
    seen = set()
    for p in Path(root).rglob("*"):
        if not p.is_file():
            continue
        if any(part in {".git", ".venv", "node_modules", ".codesmells", "__pycache__"} for part in p.parts):
            continue
        lang = _LANG_BY_EXT.get(p.suffix)
        if lang:
            seen.add(lang)
    return seen


def library_rules_for_languages(langs: set[str]) -> list[Rule]:
    """Return library rules whose `lang` intersects `langs` OR whose lang is empty/['any']."""
    rules = _load_library_rules()
    out = []
    for r in rules:
        rlangs = set(r.lang)
        if not rlangs or "any" in rlangs or rlangs & langs:
            out.append(r)
    return out


def _load_library_rules() -> list[Rule]:
    rules = []
    try:
        pkg = importlib.resources.files("codesmells.library")
    except (FileNotFoundError, ModuleNotFoundError):
        return rules
    for child in pkg.iterdir():
        if not child.is_dir():
            continue
        for entry in child.iterdir():
            if entry.name.endswith(".smell.md"):
                with importlib.resources.as_file(entry) as p:
                    try:
                        rules.append(parse_rule_file(p))
                    except RuleParseError as e:
                        print(f"warn: library rule {entry.name}: {e}", file=sys.stderr)
    return rules

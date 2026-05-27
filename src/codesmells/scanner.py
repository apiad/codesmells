import hashlib
import re
from pathlib import Path
from codesmells.types import Rule, Finding
from codesmells.lexer import ProbabilisticLexer
from codesmells.alignment import FuzzyAlignmentEngine


_TAU_SAFE = 0.7
_SOURCE_EXTS = {".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".rs", ".java", ".rb"}


def scan_path(root: Path, rules: list[Rule]) -> list[Finding]:
    """Scan every source file under root against every rule; return all findings."""
    findings: list[Finding] = []
    lexer = ProbabilisticLexer()
    engine = FuzzyAlignmentEngine()
    for f in _iter_source_files(Path(root)):
        try:
            text = f.read_text()
        except UnicodeDecodeError:
            continue
        findings.extend(_scan_file(f, text, rules, lexer, engine))
    return findings


def _iter_source_files(root: Path):
    if root.is_file():
        yield root
        return
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        if any(part in {".git", ".venv", "node_modules", ".codesmells", "__pycache__"} for part in p.parts):
            continue
        if p.suffix in _SOURCE_EXTS:
            yield p


def _scan_file(file_path: Path, text: str, rules: list[Rule], lexer, engine) -> list[Finding]:
    file_tokens = lexer.tokenize(text)
    if not file_tokens:
        return []
    ignore_set = _harvest_ignores(text, file_path.suffix)
    out: list[Finding] = []
    # Track per-rule range coverage to dedup overlapping matches
    rule_ranges: dict[str, list[tuple[int, int]]] = {}

    for rule in rules:
        if any(pf not in text for pf in rule.pre_filters):
            continue
        for anti in rule.anti_patterns:
            anti_tokens = lexer.tokenize(anti)
            if not anti_tokens:
                continue
            window_size = 2 * len(anti_tokens)
            stride = max(1, len(anti_tokens) // 2)
            for window_start in range(0, len(file_tokens), stride):
                window = file_tokens[window_start:window_start + window_size]
                if len(window) < len(anti_tokens):
                    continue
                score, bindings, indices = engine.align(window, anti_tokens)
                if score < rule.tau or not indices:
                    continue

                abs_start = window_start + indices[0]
                abs_end = window_start + indices[1]
                anchor_line = file_tokens[abs_start].line_num
                end_line = file_tokens[abs_end].line_num

                # Ignore if any line in the match range is in the ignore_set
                if any((rule.id, ln) in ignore_set for ln in range(anchor_line, end_line + 1)):
                    continue

                if _matches_any_safe(file_tokens, abs_start, abs_end, rule, lexer, engine):
                    continue

                # Dedup: skip if this range overlaps an existing finding for the same rule
                existing = rule_ranges.setdefault(rule.id, [])
                if any(not (end_line < a or anchor_line > b) for a, b in existing):
                    continue
                existing.append((anchor_line, end_line))

                snippet = _build_snippet(text, anchor_line, end_line)
                fid = _finding_id(rule.id, str(file_path), anchor_line, snippet)
                out.append(Finding(
                    id=fid,
                    rule_id=rule.id,
                    file_path=str(file_path),
                    anchor_line=anchor_line,
                    end_line=end_line,
                    snippet=snippet,
                    bindings=dict(bindings) if bindings else {},
                    score=score,
                ))
    return out


def _matches_any_safe(file_tokens, abs_start, abs_end, rule, lexer, engine) -> bool:
    """Check if the matched range — or a tight extension forward, if safe is longer than match —
    aligns to any Safe pattern. The extension is one-sided (forward only) so a safe pattern
    matching a NEIGHBOR doesn't suppress the current finding."""
    for safe in rule.safe_patterns:
        st = lexer.tokenize(safe)
        if not st:
            continue
        match_len = abs_end - abs_start + 1
        # Extend forward to at least cover len(safe); never backward (would absorb a neighbor)
        end = max(abs_end + 1, abs_start + len(st))
        end = min(end, len(file_tokens))
        safe_window = file_tokens[abs_start:end]
        s, _, _ = engine.align(safe_window, st)
        if s >= _TAU_SAFE:
            return True
    return False


def _harvest_ignores(text: str, suffix: str) -> set[tuple[str, int]]:
    """Return a set of (rule_id, line) the ignore applies to (own line + next non-blank)."""
    out: set[tuple[str, int]] = set()
    lines = text.splitlines()
    comment_prefix = _comment_prefix(suffix)
    pattern = re.compile(re.escape(comment_prefix) + r"\s*codesmells:\s*ignore\s+(\S+)")
    for i, line in enumerate(lines, start=1):
        m = pattern.search(line)
        if not m:
            continue
        rule_id = m.group(1).rstrip(",")
        out.add((rule_id, i))
        for j in range(i + 1, len(lines) + 1):
            if lines[j - 1].strip():
                out.add((rule_id, j))
                break
    return out


def _comment_prefix(suffix: str) -> str:
    if suffix in {".js", ".ts", ".tsx", ".jsx", ".go", ".rs", ".java"}:
        return "//"
    return "#"


def _build_snippet(text: str, anchor_line: int, end_line: int, context: int = 5) -> str:
    lines = text.splitlines()
    start = max(0, anchor_line - 1 - context)
    end = min(len(lines), end_line + context)
    return "\n".join(lines[start:end])


def _finding_id(rule_id: str, file_path: str, anchor_line: int, snippet: str) -> str:
    canonical = re.sub(r"\s+", " ", snippet).strip()
    payload = f"{rule_id}:{file_path}:{anchor_line}:{canonical}"
    return hashlib.md5(payload.encode()).hexdigest()[:8]

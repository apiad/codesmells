import json
import yaml
import re
from pathlib import Path
from typing import List, Optional
from codesmells.models import Rule, Candidate

class StorageManager:
    def __init__(self, root_dir: str = ".codesmells"):
        self.root_dir = Path(root_dir)
        self.root_dir.mkdir(exist_ok=True)
        self.session_file = self.root_dir / "session.json"
        self._ensure_session_exists()

    def _ensure_session_exists(self):
        if not self.session_file.exists():
            with open(self.session_file, 'w') as f:
                json.dump({"candidates": []}, f)

    def save_candidates(self, candidates: List[Candidate]):
        """
        Saves a list of candidates to the session.json file.
        """
        data = {"candidates": [self._candidate_to_dict(c) for c in candidates]}
        with open(self.session_file, 'w') as f:
            json.dump(data, f, indent=2)

    def load_candidates(self) -> List[Candidate]:
        """
        Loads all candidates from the session.json file.
        """
        if not self.session_file.exists():
            return []
        
        with open(self.session_file, 'r') as f:
            data = json.load(f)
        
        return [self._dict_to_candidate(c) for c in data.get("candidates", [])]

    def update_candidate_status(self, candidate_id: str, status: str):
        """
        Updates the status of a specific candidate in the session.json file.
        """
        candidates = self.load_candidates()
        for c in candidates:
            if c.id == candidate_id:
                c.status = status
                break
        self.save_candidates(candidates)

    def _candidate_to_dict(self, c: Candidate) -> dict:
        return {
            "id": c.id,
            "rule_id": c.rule_id,
            "file_path": c.file_path,
            "line_num": c.line_num,
            "raw_snippet": c.raw_snippet,
            "status": c.status,
            "bindings": [
                {
                    "candidate_id": b.candidate_id,
                    "sigil": b.sigil,
                    "bound_value": b.bound_value
                } for b in c.bindings
            ]
        }

    def _dict_to_candidate(self, d: dict) -> Candidate:
        from codesmells.models import Binding
        bindings = [
            Binding(
                candidate_id=b["candidate_id"],
                sigil=b["sigil"],
                bound_value=b["bound_value"]
            ) for b in d.get("bindings", [])
        ]
        return Candidate(
            id=d["id"],
            rule_id=d["rule_id"],
            file_path=d["file_path"],
            line_num=d["line_num"],
            raw_snippet=d["raw_snippet"],
            status=d["status"],
            bindings=bindings
        )

    def load_rules(self, path: str) -> List[Rule]:
        """
        Loads all .smell.md rules from a directory or a single file.
        """
        rules = []
        path_obj = Path(path)
        if path_obj.is_dir():
            files = list(path_obj.glob("*.smell.md"))
        else:
            files = [path_obj] if path_obj.name.endswith(".smell.md") else []

        for f in files:
            rules.append(self._parse_rule_file(f))
        return rules

    def _parse_rule_file(self, file_path: Path) -> Rule:
        """
        Parses a single .smell.md file into a Rule object.
        """
        content = file_path.read_text()
        
        # Split YAML frontmatter from Markdown
        frontmatter = {}
        markdown_content = content
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                try:
                    frontmatter = yaml.safe_load(parts[1]) or {}
                except yaml.YAMLError:
                    frontmatter = {}
                markdown_content = parts[2]
        
        # ID is the filename without .smell.md
        rule_id = file_path.name
        if rule_id.endswith(".smell.md"):
            rule_id = rule_id[:-9]
            
        pre_filters = frontmatter.get("pre_filters", [])
        tau = frontmatter.get("tau", 0.8)
        
        anti_patterns = self._extract_code_blocks(markdown_content, "### Anti-Pattern")
        safe_patterns = self._extract_code_blocks(markdown_content, "### Safe")
        refactor_templates = self._extract_code_blocks(markdown_content, "### Refactoring")
        
        refactor_template = refactor_templates[0] if refactor_templates else None
        
        return Rule(
            id=rule_id,
            tau=tau,
            pre_filters=pre_filters,
            anti_patterns=anti_patterns,
            safe_patterns=safe_patterns,
            refactor_template=refactor_template
        )

    def _extract_code_blocks(self, content: str, header: str) -> List[str]:
        """
        Extracts code blocks from a Markdown section defined by a header.
        """
        # We look for the header and then capture everything until the next header of same or higher level
        # A simpler way: split by the header
        parts = content.split(header)
        if len(parts) < 2:
            return []
        
        blocks = []
        # For each part after the header
        for part in parts[1:]:
            # Find the next header (starts with # at the beginning of a line)
            # Or just assume the section ends when the next "###" or "##" or "#" appears
            # But the prompt specifically mentions ### headers.
            
            # Look for next header
            match = re.search(r"\n#", part)
            section = part[:match.start()] if match else part
            
            # Find code blocks within the section
            # Matches ``` followed by optional language then newline then code then newline then ```
            code_matches = re.findall(r"```(?:\w+)?\n(.*?)\n```", section, re.DOTALL)
            for code in code_matches:
                blocks.append(code.strip())
            
        return blocks

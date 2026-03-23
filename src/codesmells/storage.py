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
        # TODO: Implement JSON storage
        pass

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

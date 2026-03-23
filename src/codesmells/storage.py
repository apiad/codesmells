import json
from pathlib import Path
from typing import List
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
        # TODO: Implement YAML/MD parser
        return []

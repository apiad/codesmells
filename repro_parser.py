import re
from typing import List

def _extract_code_blocks(content: str, header: str) -> List[str]:
    parts = content.split(header)
    if len(parts) < 2:
        return []
    blocks = []
    for part in parts[1:]:
        match = re.search(r"\n##+ ", part)
        section = part[:match.start()] if match else part
        code_matches = re.findall(r"```(?:\w+)?\n(.*?)\n```", section, re.DOTALL)
        for code in code_matches:
            blocks.append(code.strip())
    return blocks

content = """### Refactoring

Using a more specific exception (like `ValueError` or a custom exception) ensures that only the errors you're prepared to handle are caught, while letting others propagate and be properly diagnosed.

```python
try:
    ...
# TODO: Replace ValueError with the specific expected exception type.
except ValueError as $VAR:
    ...
```
"""

blocks = _extract_code_blocks(content, "### Refactoring")
print(f"Found {len(blocks)} blocks")
for i, b in enumerate(blocks):
    print(f"Block {i+1}:")
    print(b)
    print("-" * 10)

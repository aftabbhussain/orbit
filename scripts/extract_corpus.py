import sys
import json
from pathlib import Path

root_path = Path(__file__).parent.parent.resolve()
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

from loguru import logger

def write_jsonl(records, output_path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")

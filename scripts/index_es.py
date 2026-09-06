import sys
from pathlib import Path
root_path = Path(__file__).parent.parent.resolve()
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

INDEX_NAME = "arxiv_documents"
INDEX_MAPPINGS = {
    "settings": {
        "analysis": {
            "analyzer": {
                "default": {
                    "type": "standard"
                }
            }
        }
    }
}

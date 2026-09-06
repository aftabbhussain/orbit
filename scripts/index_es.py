import argparse
import json
import sys
from pathlib import Path

project_dir = Path(__file__).parent.parent.resolve()
if str(project_dir) not in sys.path:
    sys.path.insert(0, str(project_dir))

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from tqdm import tqdm
from backend.settings.environment import settings

CORPUS_PATH = project_dir / "data" / "processed" / "arxiv_documents.jsonl"

MAPPING_CONFIGURATION = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0,
    },
    "mappings": {
        "properties": {
            "paper_id": {"type": "keyword"},
            "section": {"type": "keyword"},
            "content_type": {"type": "keyword"},
            "page_info": {"type": "integer"},
            "year": {"type": "integer"},
            "content": {"type": "text"},
            "title": {"type": "text"},
        }
    },
}


def read_corpus_records() -> list[dict]:
    if not CORPUS_PATH.exists():
        print(f"[ERROR] Processed corpus not found at: {CORPUS_PATH}")
        sys.exit(1)

    records = []
    with open(CORPUS_PATH, encoding="utf-8") as f:
        for row in f:
            stripped = row.strip()
            if stripped:
                records.append(json.loads(stripped))
    return records


def initialize_index(client: Elasticsearch, index_name: str) -> None:
    if client.indices.exists(index=index_name):
        print(f"[INFO] Index '{index_name}' already present.")
        return

    print(f"[INFO] Creating index '{index_name}'...")
    client.indices.create(index=index_name, body=MAPPING_CONFIGURATION)
    mapping = client.indices.get_mapping(index=index_name)
    fields = mapping[index_name]["mappings"]["properties"]
    print(f"[INFO] Index configured with properties: {', '.join(sorted(fields.keys()))}")


def stream_index_documents(
    client: Elasticsearch, documents: list[dict], index_name: str
) -> None:
    action_batch = []
    for doc in documents:
        action_batch.append(
            {
                "_index": index_name,
                "_id": doc["id"],
                "_source": {
                    "content": doc["content"],
                    "paper_id": doc["paper_id"],
                    "title": doc["title"],
                    "year": doc["year"],
                    "section": doc["section"],
                    "content_type": doc["content_type"],
                    "page_info": doc["page_info"],
                },
            }
        )

    indexed_count, failed_items = bulk(
        client,
        tqdm(action_batch, desc="Ingesting"),
        chunk_size=100,
        request_timeout=120,
        raise_on_error=False,
    )

    err_count = len(failed_items) if isinstance(failed_items, list) else failed_items
    print(f"[INFO] Ingestion complete. Indexed: {indexed_count}, Errors: {err_count}")

    client.indices.refresh(index=index_name)
    total_docs = client.count(index=index_name)["count"]
    print(f"[INFO] Total verified documents: {total_docs}")


def main() -> None:
    cli_parser = argparse.ArgumentParser(description="Elasticsearch management utility")
    cli_parser.add_argument(
        "action", choices=["setup", "index", "recreate"], help="Operation to execute"
    )
    args = cli_parser.parse_args()

    es = Elasticsearch(settings.elasticsearch.url, request_timeout=60)
    target_idx = settings.elasticsearch.index

    server_info = es.info()
    print(f"[INFO] Connected to Elasticsearch v{server_info['version']['number']}")

    if args.action == "setup":
        initialize_index(es, target_idx)

    elif args.action == "index":
        if not es.indices.exists(index=target_idx):
            print(f"[ERROR] Index '{target_idx}' does not exist. Run setup first.")
            sys.exit(1)
        data = read_corpus_records()
        print(f"[INFO] Loaded {len(data)} items from {CORPUS_PATH}")
        stream_index_documents(es, data, target_idx)

    elif args.action == "recreate":
        if es.indices.exists(index=target_idx):
            print(f"[INFO] Dropping existing index '{target_idx}'...")
            client_del = es.indices.delete(index=target_idx)
        initialize_index(es, target_idx)
        data = read_corpus_records()
        print(f"[INFO] Loaded {len(data)} items from {CORPUS_PATH}")
        stream_index_documents(es, data, target_idx)

    print("[INFO] Elasticsearch procedure finished.")


if __name__ == "__main__":
    main()

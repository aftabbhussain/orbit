import argparse
import json
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from qdrant_client import QdrantClient, models
from tqdm import tqdm

base_dir = Path(__file__).parent.parent.resolve()
if str(base_dir) not in sys.path:
    sys.path.insert(0, str(base_dir))

load_dotenv()

SERVER_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
AUTH_SECRET = os.getenv("QDRANT_API_KEY", None)
TARGET_COLLECTION = os.getenv("QDRANT_COLLECTION", "arxiv_papers")
CORPUS_FILE = base_dir / "data" / "processed" / "arxiv_documents.jsonl"

VECTOR_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
DIMENSION_SIZE = 384
VECTOR_NAME = "dense"


def load_corpus() -> list[dict]:
    if not CORPUS_FILE.exists():
        print(f"[ERROR] Processed corpus not found: {CORPUS_FILE}")
        sys.exit(1)

    items = []
    with open(CORPUS_FILE, encoding="utf-8") as stream:
        for line in stream:
            clean_line = line.strip()
            if clean_line:
                items.append(json.loads(clean_line))
    return items


def configure_collection(client: QdrantClient) -> None:
    if client.collection_exists(TARGET_COLLECTION):
        print(f"[INFO] Collection '{TARGET_COLLECTION}' already exists.")
        return

    print(f"[INFO] Initializing collection '{TARGET_COLLECTION}'...")
    client.create_collection(
        collection_name=TARGET_COLLECTION,
        vectors_config={
            VECTOR_NAME: models.VectorParams(
                size=DIMENSION_SIZE, distance=models.Distance.COSINE
            )
        },
    )

    for field_name in ["paper_id", "section"]:
        client.create_payload_index(
            collection_name=TARGET_COLLECTION,
            field_name=field_name,
            field_schema=models.PayloadSchemaType.KEYWORD,
        )

    for int_field in ["page_info", "year"]:
        client.create_payload_index(
            collection_name=TARGET_COLLECTION,
            field_name=int_field,
            field_schema=models.PayloadSchemaType.INTEGER,
        )

    print(f"[INFO] Collection '{TARGET_COLLECTION}' configured successfully.")


def populate_collection(
    client: QdrantClient, dataset: list[dict], batch_size: int = 32
) -> None:
    total_records = len(dataset)
    print(f"[INFO] Ingesting {total_records} documents (batch_size={batch_size})...")

    for cursor in tqdm(range(0, total_records, batch_size), desc="Ingesting"):
        slice_chunk = dataset[cursor : cursor + batch_size]
        batch_points = []

        for row in slice_chunk:
            doc_body = row["content"]
            pt = models.PointStruct(
                id=row["id"],
                vector={
                    VECTOR_NAME: models.Document(text=doc_body, model=VECTOR_MODEL)
                },
                payload={
                    "content": doc_body,
                    "paper_id": row["paper_id"],
                    "title": row["title"],
                    "year": row["year"],
                    "section": row["section"],
                    "content_type": row["content_type"],
                    "page_info": row["page_info"],
                },
            )
            batch_points.append(pt)

        client.upsert(
            collection_name=TARGET_COLLECTION,
            points=batch_points,
            wait=True,
        )

    print(f"[INFO] Successfully indexed {total_records} points.")


def main() -> None:
    cli_parser = argparse.ArgumentParser(description="Qdrant store manager")
    cli_parser.add_argument(
        "action", choices=["setup", "index", "recreate"], help="Operation to run"
    )
    cli_parser.add_argument(
        "--batch-size", type=int, default=32, help="Batch chunk size"
    )
    parsed_args = cli_parser.parse_args()

    print(f"[INFO] Connecting to Qdrant at {SERVER_URL}...")
    client = QdrantClient(url=SERVER_URL, api_key=AUTH_SECRET)

    if parsed_args.action == "setup":
        configure_collection(client)

    elif parsed_args.action == "index":
        if not client.collection_exists(TARGET_COLLECTION):
            print(f"[ERROR] Collection '{TARGET_COLLECTION}' missing. Run setup first.")
            sys.exit(1)
        data = load_corpus()
        populate_collection(client, data, batch_size=parsed_args.batch_size)

    elif parsed_args.action == "recreate":
        if client.collection_exists(TARGET_COLLECTION):
            print(f"[INFO] Deleting existing collection '{TARGET_COLLECTION}'...")
            client.delete_collection(TARGET_COLLECTION)
        configure_collection(client)
        data = load_corpus()
        populate_collection(client, data, batch_size=parsed_args.batch_size)

    print("[INFO] Qdrant procedure completed.")


if __name__ == "__main__":
    main()

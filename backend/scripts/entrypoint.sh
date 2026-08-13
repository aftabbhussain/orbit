#!/bin/sh
set -e

if [ ! -f /app/.indexed ]; then
    echo "[INFO] First start detected - verifying index status..."

    echo "[WAIT] Connecting to Qdrant..."
    until python -c "from qdrant_client import QdrantClient; QdrantClient('${QDRANT_URL:-http://qdrant:6333}').get_collections()" 2>/dev/null; do
        echo "       Qdrant unavailable, polling in 2s..."
        sleep 2
    done
    echo "[OK] Qdrant connection established."

    echo "[WAIT] Connecting to Elasticsearch..."
    until python -c "from elasticsearch import Elasticsearch; es = Elasticsearch('${ES_URL:-http://elasticsearch:9200}'); exit(0 if es.ping() else 1)" 2>/dev/null; do
        echo "       Elasticsearch unavailable, polling in 2s..."
        sleep 2
    done
    echo "[OK] Elasticsearch connection established."

    if [ ! -d /app/data/raw ] || [ -z "$(ls -A /app/data/raw/*.pdf 2>/dev/null)" ]; then
        echo "[INFO] Pulling source documents from arXiv..."
        python scripts/fetch_papers.py || echo "[WARN] Fetch papers completed with warnings"
    else
        echo "[INFO] Existing raw documents found, bypassing download."
    fi

    if [ -d /app/data/raw ] && [ -n "$(ls -A /app/data/raw/*.pdf 2>/dev/null)" ]; then
        if [ ! -f /app/data/processed/arxiv_documents.jsonl ] || [ ! -s /app/data/processed/arxiv_documents.jsonl ]; then
            echo "[INFO] Parsing raw PDFs into text chunks..."
            python scripts/extract_corpus.py || echo "[WARN] Document parsing encountered warnings"
        else
            echo "[INFO] Preprocessed corpus detected (arxiv_documents.jsonl), skipping parse step."
        fi
    fi

    echo "[INFO] Configuring Qdrant collections..."
    python scripts/index_qdrant.py setup || echo "[WARN] Qdrant collection setup skipped"

    echo "[INFO] Configuring Elasticsearch indices..."
    python scripts/index_es.py setup || echo "[WARN] Elasticsearch index setup skipped"

    if [ -f /app/data/processed/arxiv_documents.jsonl ] && [ -s /app/data/processed/arxiv_documents.jsonl ]; then
        echo "[INFO] Ingesting documents to vector and lexical stores..."
        python scripts/index_qdrant.py index || echo "[WARN] Qdrant ingestion had warnings"
        python scripts/index_es.py index || echo "[WARN] Elasticsearch ingestion had warnings"
    else
        echo "[WARN] No preprocessed corpus available to index."
    fi

    touch /app/.indexed
    echo "[OK] Setup completed successfully. Launching server..."
else
    echo "[INFO] Store already indexed, skipping setup routine."
    echo "[INFO] Launching server..."
fi

exec "$@"

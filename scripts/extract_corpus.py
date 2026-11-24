import sys
from pathlib import Path

root_path = Path(__file__).parent.parent.resolve()
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

from loguru import logger
from backend.pipeline.pdf_extractor import process_pdfs_batch

RAW_FOLDER = Path("data/raw")
OUTPUT_CORPUS = Path("data/processed/arxiv_documents.jsonl")


def main() -> None:
    if not RAW_FOLDER.exists():
        logger.error(f"Target folder not found: {RAW_FOLDER}")
        sys.exit(1)

    pdf_collection = list(RAW_FOLDER.glob("*.pdf"))
    if not pdf_collection:
        logger.error(f"No PDF files found inside {RAW_FOLDER}")
        sys.exit(1)

    logger.info(f"Discovered {len(pdf_collection)} PDF files in {RAW_FOLDER}")
    process_pdfs_batch(RAW_FOLDER, OUTPUT_CORPUS)

    if not OUTPUT_CORPUS.exists():
        logger.error("Corpus extraction failed: destination file missing.")
        sys.exit(1)

    total_lines = sum(1 for _ in open(OUTPUT_CORPUS, encoding="utf-8"))
    size_mb = OUTPUT_CORPUS.stat().st_size / (1024 * 1024)
    logger.info(f"Output generated: {OUTPUT_CORPUS} ({size_mb:.2f} MB, {total_lines} chunks)")


if __name__ == "__main__":
    main()

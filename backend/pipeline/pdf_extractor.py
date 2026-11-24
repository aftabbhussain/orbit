import gc
import json
import logging
from pathlib import Path
from typing import Any, cast

from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend
from docling.datamodel.accelerator_options import AcceleratorDevice, AcceleratorOptions
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import (
    EasyOcrOptions,
    PdfPipelineOptions,
    TableFormerMode,
    TableStructureOptions,
)
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling_core.transforms.chunker.hybrid_chunker import HybridChunker
from docling_core.types.doc.labels import DocItemLabel
from loguru import logger

BASE_TOKENIZER = "sentence-transformers/all-MiniLM-L6-v2"


def build_doc_converter() -> DocumentConverter:
    pipeline_conf = PdfPipelineOptions(
        do_ocr=False,
        do_table_structure=True,
        table_structure_options=TableStructureOptions(
            do_cell_matching=True, mode=TableFormerMode.ACCURATE
        ),
        ocr_options=EasyOcrOptions(lang=["en"]),
        accelerator_options=AcceleratorOptions(
            num_threads=2, device=AcceleratorDevice.CPU
        ),
    )
    return DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(
                pipeline_options=pipeline_conf, backend=PyPdfiumDocumentBackend
            )
        }
    )


def read_title_header(doc) -> str:
    for item, _ in doc.iterate_items():
        if getattr(item, "label", None) == DocItemLabel.SECTION_HEADER:
            return item.text
    return ""


def parse_publication_year(paper_id: str) -> int | None:
    try:
        yr_prefix = int(paper_id[:2])
        return 1900 + yr_prefix if yr_prefix >= 90 else 2000 + yr_prefix
    except (ValueError, TypeError, IndexError):
        return None


def read_chunk_attributes(chunk) -> dict[str, Any]:
    attr_map = {"headings": [], "page_info": None, "content_type": None}
    if not hasattr(chunk, "meta"):
        return attr_map

    meta_obj = chunk.meta
    if hasattr(meta_obj, "headings") and meta_obj.headings:
        attr_map["headings"] = meta_obj.headings

    if hasattr(meta_obj, "doc_items") and meta_obj.doc_items:
        for it in meta_obj.doc_items:
            if hasattr(it, "label"):
                attr_map["content_type"] = str(it.label)
            if hasattr(it, "prov") and it.prov:
                for prov_entry in it.prov:
                    if hasattr(prov_entry, "page_no"):
                        attr_map["page_info"] = prov_entry.page_no
    return attr_map


def process_pdf(
    pdf_path: str | Path, paper_id: str | None = None
) -> list[dict[str, Any]]:
    path = Path(pdf_path)
    paper_key = paper_id or path.stem
    logger.info(f"Parsing document: {path.name}")

    try:
        converted_doc = build_doc_converter().convert(str(path)).document
    except Exception as exc:
        logger.error(f"Conversion failed for {path}: {exc}")
        return []

    title = read_title_header(converted_doc) or paper_key
    pub_year = parse_publication_year(paper_key)

    try:
        segmented_chunks = list(
            HybridChunker(tokenizer=cast(Any, BASE_TOKENIZER)).chunk(converted_doc)
        )
    except Exception as exc:
        logger.error(f"Chunking failed for {path}: {exc}")
        return []

    processed_units = []
    for idx, piece in enumerate(segmented_chunks):
        attrs = read_chunk_attributes(piece)
        headings = attrs["headings"]
        processed_units.append(
            {
                "id": idx,
                "content": piece.text,
                "paper_id": paper_key,
                "title": title,
                "year": pub_year,
                "section": headings[-1] if headings else "Unknown",
                "content_type": attrs["content_type"],
                "page_info": attrs["page_info"],
            }
        )

    logger.info(f"Generated {len(processed_units)} chunks for '{title}'")
    return processed_units


def process_pdfs_batch(
    pdf_dir: str | Path, output_path: str | Path | None = None
) -> list[dict[str, Any]]:
    folder = Path(pdf_dir)
    pdf_files = sorted(folder.glob("*.pdf"))

    if not pdf_files:
        logger.warning(f"No PDF files present in directory: {folder}")
        return []

    logger.info(f"Discovered {len(pdf_files)} PDFs in {folder}")

    if output_path:
        out_file = Path(output_path)
        out_file.parent.mkdir(parents=True, exist_ok=True)
        if out_file.exists():
            out_file.unlink()
        logger.info(f"Streaming outputs to: {out_file}")

    chunk_counter = 0
    total_accumulated = 0

    for idx, target_pdf in enumerate(pdf_files, 1):
        try:
            logger.info(f"[{idx}/{len(pdf_files)}] Parsing: {target_pdf.name}")
            records = process_pdf(target_pdf)

            for rec in records:
                rec["id"] = chunk_counter
                chunk_counter += 1

            if output_path and records:
                with open(output_path, "a", encoding="utf-8") as writer:
                    for rec in records:
                        writer.write(json.dumps(rec, ensure_ascii=False) + "\n")

            batch_count = len(records)
            total_accumulated += batch_count
            logger.info(
                f"[{idx}/{len(pdf_files)}] Processed {batch_count} chunks from {target_pdf.name}"
            )

            del records
            gc.collect()

        except Exception as err:
            logger.error(
                f"[{idx}/{len(pdf_files)}] Error parsing {target_pdf.name}: {err}"
            )

    logger.info(f"Completed extraction: {total_accumulated} total chunks indexed")
    return []


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    process_pdfs_batch("data/raw", "data/processed/arxiv_documents.jsonl")

from __future__ import annotations
import time
from pathlib import Path
import requests
from loguru import logger

CURATED_PAPERS = [
    "1706.03762",
    "1810.04805",
    "2005.14165",
    "2412.19437",
    "2501.12948",
    "2301.05908",
    "2302.13971",
    "2407.21783",
    "2301.13688",
    "2301.14185",
    "2310.06825",
    "2412.15115",
    "2407.10671",
    "2409.12186",
    "2409.12122",
    "2103.00020",
    "2112.10752",
    "2204.08381",
    "2201.11903",
    "2210.03629",
    "2205.14135",
    "2106.09685",
    "2203.02155",
    "2410.21276",
    "2212.07125",
    "2301.00952",
    "2301.02661",
    "2301.04844",
    "2301.03741",
    "2301.13636",
    "2212.14878",
    "2301.16389",
    "2301.07611",
    "2004.04906",
    "2005.11401",
    "1907.11692",
    "1910.02054",
    "1910.10683",
    "2009.03356",
    "2010.05923",
    "2010.14701",
    "2104.08651",
    "2107.03311",
    "2109.01669",
    "2110.05429",
    "2112.13792",
    "2201.04118",
    "2201.04230",
    "2201.10023",
    "2202.05431",
    "2202.11296",
    "2202.13628",
    "2203.05407",
    "2203.05486",
    "2203.07758",
    "2203.10555",
    "2204.01686",
    "2204.02311",
    "2204.04521",
    "2204.05037",
    "2204.06125",
    "2204.07314",
    "2204.10156",
    "2204.11824",
    "2205.01009",
    "2205.04145",
    "2205.11469",
    "2205.14389",
    "2205.15240",
    "2206.00661",
    "2206.07631",
    "2206.10624",
    "2206.11147",
    "2206.14822",
    "2207.01750",
    "2207.07411",
    "2207.13220",
    "2208.00063",
    "2208.01871",
    "2208.10845",
    "2208.12409",
    "2208.13261",
    "2209.00655",
    "2209.03629",
    "2209.06761",
    "2209.10685",
    "2209.11314",
    "2209.12986",
    "2210.11091",
    "2210.14822",
    "2210.14932",
    "2210.16468",
    "2211.02081",
    "2211.02318",
    "2211.04137",
    "2211.05105",
    "2211.15841",
    "2212.00794",
    "2212.01394",
    "2212.02478",
    "2212.02672",
    "2212.05641",
    "2212.07125",
    "2212.09856",
    "2212.10557",
    "2212.12085",
    "2212.13193",
    "2212.13301",
    "2212.14037",
    "2212.14558",
]


def retrieve_single_paper(arxiv_id: str, dest_dir: Path) -> bool:
    download_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
    target_file = dest_dir / f"{arxiv_id}.pdf"

    if target_file.exists():
        logger.info(f"Target paper {arxiv_id} already on disk, skipping.")
        return True

    try:
        logger.info(f"Fetching paper: {arxiv_id}")
        resp = requests.get(download_url, timeout=60, stream=True)
        resp.raise_for_status()

        with open(target_file, "wb") as handler:
            for piece in resp.iter_content(chunk_size=8192):
                handler.write(piece)

        logger.info(f"Saved: {arxiv_id}")
        return True
    except requests.exceptions.RequestException as err:
        logger.error(f"Download failed for {arxiv_id}: {err}")
        return False


def main():
    target_dir = Path("data/raw")
    target_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Initiating download for {len(CURATED_PAPERS)} papers into {target_dir}")

    downloaded = 0
    total = len(CURATED_PAPERS)

    for i, paper_id in enumerate(CURATED_PAPERS, 1):
        logger.info(f"[{i}/{total}] {paper_id}")
        if retrieve_single_paper(paper_id, target_dir):
            downloaded += 1

        if i < total:
            time.sleep(2.0)

    logger.info(f"Download finished: {downloaded}/{total} papers retrieved successfully.")


if __name__ == "__main__":
    main()

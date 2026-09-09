from collections import defaultdict
from loguru import logger

class HybridRanker:
    def fuse_candidates(self, dense_hits, sparse_hits):
        logger.debug("Merging candidate lists with RRF")
        return []

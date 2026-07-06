"""Embedding generation for conversation memory.

Produces vector representations of text using a lightweight,
dependency-free approach (word-level frequency features).  These
embeddings are consumed by ``memory/vectordb.py`` for semantic recall.

A future Build may replace this with a proper embedding model
(e.g. ``sentence-transformers``) without changing the ``VectorDB``
interface.
"""

from __future__ import annotations

import math
import re
from collections import Counter

# Common English stop-words filtered out during vectorisation.
_STOP_WORDS: set[str] = {
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to",
    "for", "of", "with", "by", "from", "as", "is", "was", "are",
    "were", "be", "been", "being", "have", "has", "had", "do",
    "does", "did", "will", "would", "can", "could", "may", "might",
    "shall", "should", "not", "no", "nor", "so", "if", "it", "its",
    "that", "this", "these", "those", "i", "me", "my", "we", "our",
    "you", "your", "he", "him", "his", "she", "her", "they", "them",
    "their", "what", "which", "who", "whom", "when", "where", "why",
    "how", "all", "each", "every", "both", "few", "more", "most",
    "some", "any", "other", "such", "only", "own", "same", "very",
    "just", "about", "up", "out", "over", "after", "before", "between",
    "under", "above", "below",
}

# Characters allowed in tokens.
_TOKEN_PATTERN = re.compile(r"[a-zA-Z0-9']+")


class Embeddings:
    """Generates sparse frequency vector "embeddings" from text.

    The vector is a ``dict[str, float]`` mapping tokens to normalised
    term-frequency values.  This is suitable for cosine-similarity
    comparison in ``VectorDB`` without requiring numpy or a model
    download.

    Usage::

        emb = Embeddings()
        vec1 = emb.embed("hello world")
        vec2 = emb.embed("world hello")
        sim = emb.cosine_similarity(vec1, vec2)  # → 1.0
    """

    @staticmethod
    def embed(text: str) -> dict[str, float]:
        """Convert ``text`` to a sparse frequency vector.

        Args:
            text: The input string.

        Returns:
            A dict mapping tokens to their normalised frequency in
            ``text``.  Keys are lowercased tokens; values are
            ``count / sqrt(total_words)`` for L2-style normalisation.
        """
        tokens = [
            tok.lower()
            for tok in _TOKEN_PATTERN.findall(text)
            if tok.lower() not in _STOP_WORDS and len(tok) > 1
        ]
        if not tokens:
            return {}

        counts = Counter(tokens)
        norm = math.sqrt(sum(c * c for c in counts.values()))
        if norm == 0:
            return {}

        return {tok: count / norm for tok, count in counts.items()}

    @staticmethod
    def cosine_similarity(
        a: dict[str, float],
        b: dict[str, float],
    ) -> float:
        """Compute cosine similarity between two sparse vectors.

        Args:
            a: First sparse vector (as returned by ``embed()``).
            b: Second sparse vector.

        Returns:
            A float in ``[0.0, 1.0]`` (1.0 = identical direction).
        """
        if not a or not b:
            return 0.0

        common = set(a) & set(b)
        if not common:
            return 0.0

        dot = sum(a[k] * b[k] for k in common)
        # Both vectors are already L2-normalised, so the denominator is 1.
        return max(0.0, min(1.0, dot))

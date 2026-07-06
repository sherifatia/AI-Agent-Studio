"""Vector database for semantic recall of conversation content.

Stores text entries as sparse frequency vectors and supports
cosine-similarity search.  Built on ``memory.embeddings.Embeddings``
and the standard library only — no external vector database required.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from core.logging_setup import get_logger
from memory.embeddings import Embeddings

_logger = get_logger(__name__)


@dataclass
class VectorEntry:
    """A single entry stored in the vector database.

    Attributes:
        id:     Unique identifier for this entry.
        text:   The original text that was embedded.
        vector: The sparse frequency vector produced by ``Embeddings``.
        metadata: Optional key/value annotations.
    """

    id: str
    text: str
    vector: dict[str, float]
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass
class SearchResult:
    """A single search result with its similarity score.

    Attributes:
        entry:  The matched ``VectorEntry``.
        score:  Cosine similarity in ``[0.0, 1.0]``.
    """

    entry: VectorEntry
    score: float


class VectorDB:
    """In-memory vector database supporting insert and cosine search.

    Usage::

        db = VectorDB()
        db.insert("greeting", "Hello, how are you?")
        db.insert("farewell", "Goodbye, see you later.")
        results = db.search("hi there", top_k=5)
    """

    def __init__(self) -> None:
        self._entries: dict[str, VectorEntry] = {}
        self._embeddings = Embeddings()

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    def insert(
        self,
        id: str,
        text: str,
        metadata: dict[str, object] | None = None,
    ) -> VectorEntry:
        """Embed and store a text entry.

        Args:
            id:   Unique identifier.  If an entry with this ``id`` already
                  exists it is overwritten.
            text: The text to store.
            metadata: Optional key/value annotations.

        Returns:
            The created ``VectorEntry``.
        """
        vector = self._embeddings.embed(text)
        entry = VectorEntry(
            id=id,
            text=text,
            vector=vector,
            metadata=metadata or {},
        )
        self._entries[id] = entry
        _logger.debug("VectorDB: inserted '%s' (%d features)", id, len(vector))
        return entry

    def delete(self, id: str) -> None:
        """Remove an entry by its id.

        Args:
            id: The entry identifier.

        Raises:
            KeyError: If no entry with that ``id`` exists.
        """
        if id not in self._entries:
            raise KeyError(f"VectorDB: unknown id '{id}'")
        del self._entries[id]
        _logger.debug("VectorDB: deleted '%s'", id)

    def clear(self) -> None:
        """Remove all entries."""
        self._entries.clear()
        _logger.debug("VectorDB: cleared")

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def get(self, id: str) -> VectorEntry | None:
        """Return the entry with the given id, or ``None``."""
        return self._entries.get(id)

    def count(self) -> int:
        """Return the number of stored entries."""
        return len(self._entries)

    def all_entries(self) -> list[VectorEntry]:
        """Return every stored entry (order is insertion order)."""
        return list(self._entries.values())

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def search(
        self,
        query: str,
        top_k: int = 5,
        min_score: float = 0.0,
    ) -> list[SearchResult]:
        """Search for entries semantically similar to ``query``.

        Args:
            query:    The search text.
            top_k:    Maximum number of results to return.
            min_score: Minimum similarity threshold (0.0 = no filter).

        Returns:
            A list of ``SearchResult`` objects sorted by descending score.
            Empty when there are no entries or no results meet the
            threshold.
        """
        if not self._entries:
            return []

        query_vector = self._embeddings.embed(query)
        if not query_vector:
            return []

        scored: list[SearchResult] = []
        for entry in self._entries.values():
            score = self._embeddings.cosine_similarity(
                query_vector, entry.vector
            )
            if score >= min_score:
                scored.append(SearchResult(entry=entry, score=score))

        scored.sort(key=lambda r: r.score, reverse=True)
        return scored[:top_k]

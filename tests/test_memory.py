"""Tests for memory subsystems."""

import math

from memory.embeddings import Embeddings
from memory.vectordb import VectorDB

# The Embeddings class uses L2-normalised frequency vectors.
# "cat dog cat" -> {cat: 2, dog: 1}, norm = sqrt(2^2 + 1^2) = sqrt(5) ≈ 2.236
# Normalised: cat → 2/√5 ≈ 0.8944, dog → 1/√5 ≈ 0.4472


class TestEmbeddings:
    def test_empty_text_returns_empty_vector(self):
        emb = Embeddings()
        vector = emb.embed("")
        assert vector == {}

    def test_simple_text_produces_normalised_frequencies(self):
        emb = Embeddings()
        vector = emb.embed("cat dog cat")
        norm = math.sqrt(5)  # sqrt(2^2 + 1^2)
        assert vector == {"cat": 2.0 / norm, "dog": 1.0 / norm}

    def test_cosine_similarity_identical(self):
        emb = Embeddings()
        v = emb.embed("hello world")
        sim = emb.cosine_similarity(v, v)
        assert abs(sim - 1.0) < 1e-6

    def test_cosine_similarity_orthogonal(self):
        emb = Embeddings()
        v1 = emb.embed("cat")
        v2 = emb.embed("dog")
        sim = emb.cosine_similarity(v1, v2)
        assert abs(sim - 0.0) < 1e-6


class TestVectorDB:
    def test_insert_and_search(self):
        db = VectorDB()
        db.insert("id1", "cat animal")
        db.insert("id2", "dog animal")
        results = db.search("cat", top_k=1)
        assert len(results) == 1
        assert results[0].entry.id == "id1"

    def test_search_returns_all_when_top_k_large(self):
        db = VectorDB()
        db.insert("a", "apple")
        db.insert("b", "banana")
        results = db.search("fruit", top_k=10)
        assert len(results) == 2

    def test_delete_removes_entry(self):
        db = VectorDB()
        db.insert("del_me", "something")
        db.delete("del_me")
        assert db.count() == 0

    def test_delete_nonexistent_raises(self):
        db = VectorDB()
        import pytest
        with pytest.raises(KeyError):
            db.delete("nobody")

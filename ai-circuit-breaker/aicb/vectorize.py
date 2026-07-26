"""
Deterministic, dependency-free text embedding.

The AI Circuit Breaker deliberately does NOT use a second learned model to police the
first one -- a governance layer that is itself an opaque neural net just moves the trust
problem, it doesn't solve it. Instead we use a fixed, deterministic feature-hashing
transform (character n-grams -> signed hash buckets -> L2-normalized vector). This is
the same family of technique used in production text classifiers (the "hashing trick"),
and it has three properties that matter here:

  1. Deterministic: the same string always maps to the same vector. No training, no
     drift, no model version skew between the governed agent and the governor.
  2. Cheap: O(len(text)) with no GPU/network call, so it can run inline on every single
     AI action without adding meaningful latency (design target: single-digit ms).
  3. Domain-portable: works on any text -- network operation commands, ECG rhythm
     statements, customer-support replies, tool-call JSON -- without retraining.

For production deployments this module is a drop-in replacement point: swap `embed()`
for a call to your organization's approved sentence-embedding model if you want richer
semantics. The rest of the breaker only depends on `embed()` returning a fixed-length,
L2-normalized numpy vector.
"""
from __future__ import annotations

import hashlib
import re
from typing import Iterable

import numpy as np

_TOKEN_RE = re.compile(r"[a-z0-9]+")


def _char_ngrams(text: str, n: int = 3) -> Iterable[str]:
    text = f"^{text}$"
    if len(text) < n:
        yield text
        return
    for i in range(len(text) - n + 1):
        yield text[i : i + n]


def _hash_to_bucket(token: str, dim: int) -> tuple[int, int]:
    """Return (bucket_index, sign) for a token, derived from a stable sha256 hash."""
    h = hashlib.sha256(token.encode("utf-8")).digest()
    idx = int.from_bytes(h[:4], "big") % dim
    sign = 1 if (h[4] & 1) == 0 else -1
    return idx, sign


def embed(text: str, dim: int = 256) -> np.ndarray:
    """Embed arbitrary text into a fixed-length, deterministic, L2-normalized vector.

    Combines word tokens and character 3-grams so both lexical and sub-lexical
    (typo/morphology tolerant) similarity contribute to the resulting vector.
    """
    if text is None:
        text = ""
    text_lower = text.lower()
    vec = np.zeros(dim, dtype=np.float64)

    words = _TOKEN_RE.findall(text_lower)
    for w in words:
        idx, sign = _hash_to_bucket(f"w:{w}", dim)
        vec[idx] += sign * 1.0

    for ng in _char_ngrams(text_lower, n=3):
        idx, sign = _hash_to_bucket(f"g:{ng}", dim)
        vec[idx] += sign * 0.5

    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm
    return vec


def embed_many(texts: Iterable[str], dim: int = 256) -> np.ndarray:
    return np.stack([embed(t, dim=dim) for t in texts], axis=0)


def centroid(texts: Iterable[str], dim: int = 256) -> np.ndarray:
    """Compute the L2-normalized centroid ("center of gravity") of a set of reference
    texts. Used to build the Local Semantic Neighborhood / valid ontological state
    space centroid (No) referenced in the design spec's Semantic Anomaly Score.
    """
    mat = embed_many(texts, dim=dim)
    if mat.shape[0] == 0:
        return np.zeros(dim, dtype=np.float64)
    c = mat.mean(axis=0)
    norm = np.linalg.norm(c)
    if norm > 0:
        c = c / norm
    return c


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    na = np.linalg.norm(a)
    nb = np.linalg.norm(b)
    if na == 0 or nb == 0:
        return 0.0
    return float(np.dot(a, b) / (na * nb))

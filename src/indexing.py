"""
Tahap 2 - Inverted Index.

Struktur dasar:
    term -> postings list

Setiap posting menyimpan ID dokumen beserta term frequency (TF):
    index["toraja"] = {"D22": 14, "D23": 16, ...}

Dari struktur ini diperoleh:
    - postings list  : daftar ID dokumen yang mengandung term
    - TF(t, d)       : jumlah kemunculan term t di dokumen d
    - DF(t)          : jumlah dokumen yang mengandung term t
"""

import json
from collections import Counter
from pathlib import Path


class InvertedIndex:
    def __init__(self):
        self.index = {}       # term -> {doc_id: tf}
        self.doc_len = {}     # doc_id -> jumlah token dokumen

    def build(self, docs):
        """docs: dict {doc_id: [token, ...]}"""
        index = {}
        for doc_id, tokens in docs.items():
            self.doc_len[doc_id] = len(tokens)
            for term, tf in Counter(tokens).items():
                index.setdefault(term, {})[doc_id] = tf
        self.index = dict(sorted(index.items()))
        return self

    # ---------------- statistik koleksi ----------------
    @property
    def N(self):
        return len(self.doc_len)

    @property
    def avgdl(self):
        return sum(self.doc_len.values()) / self.N

    @property
    def vocabulary(self):
        return list(self.index)

    # ---------------- akses index ----------------
    def postings(self, term):
        """Postings list: ID dokumen yang mengandung term."""
        return list(self.index.get(term, {}))

    def tf(self, term, doc_id):
        return self.index.get(term, {}).get(doc_id, 0)

    def df(self, term):
        return len(self.index.get(term, {}))

    def candidates(self, terms):
        """Dokumen kandidat = gabungan postings list semua term query."""
        result = set()
        for t in terms:
            result.update(self.index.get(t, {}))
        return result

    # ---------------- simpan / muat ----------------
    def save(self, path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        data = {"N": self.N, "avgdl": self.avgdl, "doc_len": self.doc_len, "index": self.index}
        Path(path).write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    @classmethod
    def load(cls, path):
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        obj = cls()
        obj.index = data["index"]
        obj.doc_len = data["doc_len"]
        return obj

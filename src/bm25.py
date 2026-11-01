"""
Tahap 5 - BM25 (Okapi BM25), diimplementasikan sendiri.

    score(D, Q) = sum_{t in Q} IDF(t) * f(t,D) * (k1 + 1)
                                 / ( f(t,D) + k1 * (1 - b + b * |D| / avgdl) )

    IDF(t) = ln( 1 + (N - df(t) + 0.5) / (df(t) + 0.5) )

    f(t,D) : frekuensi term t di dokumen D
    |D|    : panjang dokumen (jumlah token setelah prapemrosesan)
    avgdl  : rata-rata panjang dokumen di koleksi
    k1     : mengendalikan saturasi TF (dipakai 1.2)
    b      : mengendalikan normalisasi panjang dokumen (dipakai 0.75)

Rumus dan contoh perhitungan mengikuti materi kuliah (slide BM25, contoh
query "hotel nyaman" menghasilkan D1 = 0.9400, D3 = 0.5313, D2 = 0.4043).
"""

import math


class BM25:
    def __init__(self, index, k1=1.2, b=0.75):
        self.index = index
        self.k1 = k1
        self.b = b
        self.N = index.N
        self.avgdl = index.avgdl
        self.idf = {
            t: math.log(1 + (self.N - len(p) + 0.5) / (len(p) + 0.5))
            for t, p in index.index.items()
        }

    def term_score(self, term, doc_id, tf=None):
        """Kontribusi satu term terhadap skor BM25 dokumen."""
        tf = self.index.tf(term, doc_id) if tf is None else tf
        if tf == 0 or term not in self.idf:
            return 0.0
        dl = self.index.doc_len[doc_id]
        norm = self.k1 * (1 - self.b + self.b * dl / self.avgdl)
        return self.idf[term] * tf * (self.k1 + 1) / (tf + norm)

    def score(self, query_terms, doc_id):
        return sum(self.term_score(t, doc_id) for t in query_terms)

    def search(self, query_terms, top_k=10):
        """Mengembalikan [(doc_id, skor BM25), ...] terurut dari terbesar."""
        terms = [t for t in query_terms if t in self.idf]
        if not terms:
            return []
        candidates = self.index.candidates(terms)
        scores = [(d, self.score(terms, d)) for d in candidates]
        scores = [(d, s) for d, s in scores if s > 0]
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores if top_k is None else scores[:top_k]

    def explain(self, query_terms, doc_ids):
        """Tabel rincian perhitungan BM25 per term dan dokumen."""
        rows = []
        for t in dict.fromkeys(query_terms):
            for d in doc_ids:
                tf = self.index.tf(t, d)
                dl = self.index.doc_len[d]
                rows.append({
                    "term": t, "doc_id": d, "f(t,D)": tf, "DF": self.index.df(t),
                    "|D|": dl, "|D|/avgdl": round(dl / self.avgdl, 3),
                    "IDF": round(self.idf.get(t, 0.0), 4),
                    "skor term": round(self.term_score(t, d), 4),
                })
        return rows

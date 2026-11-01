"""
Tahap 3 & 4 - TF-IDF, Vector Space Model, dan Cosine Similarity.

Rumus (sesuai materi kuliah):
    TF(t, d)      = jumlah kemunculan term t di dokumen d
    IDF(t)        = log10(N / df(t))
    TF-IDF(t, d)  = TF(t, d) x IDF(t)

Dokumen dan query direpresentasikan sebagai vektor TF-IDF dalam ruang term
(Vector Space Model). Kemiripan dihitung dengan cosine similarity:

    cos(q, d) = (q . d) / (|q| x |d|)

|d| dihitung dari SELURUH term di dokumen, sehingga dokumen panjang yang
memuat banyak term lain tidak otomatis menang.
"""

import math
from collections import Counter


class TFIDFRetrieval:
    def __init__(self, index):
        self.index = index
        self.N = index.N
        self.idf = {t: math.log10(self.N / len(p)) for t, p in index.index.items()}

        # bobot TF-IDF setiap dokumen dan panjang (norma) vektornya
        self.doc_vectors = {}
        for term, postings in index.index.items():
            for doc_id, tf in postings.items():
                self.doc_vectors.setdefault(doc_id, {})[term] = tf * self.idf[term]
        self.doc_norm = {
            d: math.sqrt(sum(w * w for w in vec.values()))
            for d, vec in self.doc_vectors.items()
        }

    # ---------------- bobot ----------------
    def weight(self, term, doc_id):
        return self.index.tf(term, doc_id) * self.idf.get(term, 0.0)

    def query_vector(self, query_terms):
        """Vektor query: TF term di query x IDF term (term di luar vocabulary diabaikan)."""
        tf_q = Counter(t for t in query_terms if t in self.idf)
        return {t: tf * self.idf[t] for t, tf in tf_q.items()}

    # ---------------- cosine & ranking ----------------
    def cosine(self, q_vec, doc_id):
        q_norm = math.sqrt(sum(w * w for w in q_vec.values()))
        if q_norm == 0 or self.doc_norm.get(doc_id, 0) == 0:
            return 0.0
        dot = sum(w * self.doc_vectors[doc_id].get(t, 0.0) for t, w in q_vec.items())
        return dot / (q_norm * self.doc_norm[doc_id])

    def search(self, query_terms, top_k=10):
        """Mengembalikan [(doc_id, skor cosine), ...] terurut dari terbesar."""
        q_vec = self.query_vector(query_terms)
        if not q_vec:
            return []
        candidates = self.index.candidates(q_vec)          # hanya dokumen di postings list
        scores = [(d, self.cosine(q_vec, d)) for d in candidates]
        scores = [(d, s) for d, s in scores if s > 0]
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores if top_k is None else scores[:top_k]

    # ---------------- penjelasan perhitungan ----------------
    def explain(self, query_terms, doc_ids):
        """Tabel perhitungan TF, DF, IDF, dan TF-IDF untuk term query pada beberapa dokumen."""
        rows = []
        for t in dict.fromkeys(query_terms):
            df = self.index.df(t)
            for d in doc_ids:
                tf = self.index.tf(t, d)
                rows.append({
                    "term": t, "doc_id": d, "TF": tf, "DF": df,
                    "IDF = log10(N/DF)": round(self.idf.get(t, 0.0), 4),
                    "TF-IDF = TF x IDF": round(tf * self.idf.get(t, 0.0), 4),
                })
        return rows

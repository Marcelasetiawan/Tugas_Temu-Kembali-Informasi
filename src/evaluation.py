"""
Tahap 7 - Evaluasi Retrieval.

Metrik untuk hasil Top-k:
    Precision@k = |relevan di Top-k| / k
    Recall@k    = |relevan di Top-k| / |seluruh dokumen relevan|
    F1@k        = 2 * P@k * R@k / (P@k + R@k)

Ground truth (dokumen relevan per query) dibaca dari evaluation/queries.csv.
"""

import pandas as pd


def load_queries(path):
    q = pd.read_csv(path)
    q["relevant"] = q["relevant_docs"].str.split(";").map(lambda xs: [x.strip() for x in xs])
    return q


def precision_at_k(ranked, relevant, k):
    return sum(1 for d in ranked[:k] if d in relevant) / k


def recall_at_k(ranked, relevant, k):
    return sum(1 for d in ranked[:k] if d in relevant) / len(relevant)


def f1(p, r):
    return 2 * p * r / (p + r) if (p + r) else 0.0


def evaluate(engine, queries, ks=(5, 10), methods=("tfidf", "bm25")):
    """Menghitung P@k, R@k, dan F1@k setiap query untuk setiap metode."""
    rows = []
    for _, q in queries.iterrows():
        relevant = set(q["relevant"])
        for m in methods:
            ranked = engine.rank_ids(q["query"], method=m, top_k=max(ks))
            row = {"qid": q["qid"], "query": q["query"], "jenis": q["jenis"],
                   "metode": "BM25" if m == "bm25" else "TF-IDF", "jumlah_relevan": len(relevant)}
            for k in ks:
                p, r = precision_at_k(ranked, relevant, k), recall_at_k(ranked, relevant, k)
                row[f"P@{k}"], row[f"R@{k}"], row[f"F1@{k}"] = p, r, f1(p, r)
            rows.append(row)
    return pd.DataFrame(rows)


def summarize(eval_df, ks=(5, 10)):
    """Rata-rata metrik per metode."""
    cols = [f"{m}@{k}" for k in ks for m in ("P", "R", "F1")]
    return eval_df.groupby("metode")[cols].mean().round(3)

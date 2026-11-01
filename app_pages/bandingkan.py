import pandas as pd
import streamlit as st

from src.app_utils import EXAMPLE_QUERIES, get_engine, search_box, show_query_info, show_results
from src.ui import steps_row

engine = get_engine()

with st.container(key="card_sky_bandingkan_1"):
    query = search_box("bnd", "Query", EXAMPLE_QUERIES, placeholder="contoh: tari topeng",
                       help="Tekan Enter untuk mencari")
    top_k = st.slider("Top-k", min_value=3, max_value=20, value=10, key="bnd_topk")

if not query.strip():
    steps_row([
        ("Ketik satu query", "Atau klik salah satu contoh berwarna di atas."),
        ("Lihat kiri dan kanan", "Kiri hasil TF-IDF + Cosine, kanan hasil BM25."),
        ("Hitung yang sama", "Kartu angka menunjukkan berapa dokumen muncul di kedua hasil."),
        ("Cek perubahan peringkat", "Tabel menunjukkan dokumen yang naik atau turun jika metode diganti."),
    ])
    st.stop()

res_t = engine.search(query, method="tfidf", top_k=top_k)
res_b = engine.search(query, method="bm25", top_k=top_k)
show_query_info(res_b)

if res_b["message"]:
    st.warning(res_b["message"], icon=":material/search_off:")
    st.stop()

ids_t = [r["doc_id"] for r in res_t["results"]]
ids_b = [r["doc_id"] for r in res_b["results"]]
same = set(ids_t) & set(ids_b)

with st.container(horizontal=True):
    st.metric(f"Dokumen sama di Top-{top_k}", f"{len(same)} dari {top_k}", border=True)
    st.metric("Peringkat 1 sama", "Ya" if ids_t[:1] == ids_b[:1] else "Tidak", border=True)
    st.metric("Hanya di TF-IDF", len(set(ids_t) - same), border=True)
    st.metric("Hanya di BM25", len(set(ids_b) - same), border=True)

tab_cards, tab_table = st.tabs(["Hasil berdampingan", "Perubahan peringkat"])

with tab_cards:
    left, right = st.columns(2)
    with left:
        st.subheader("TF-IDF + Cosine")
        show_results(res_t)
    with right:
        st.subheader("BM25")
        show_results(res_b)

with tab_table:
    rows = []
    for d in dict.fromkeys(ids_t + ids_b):
        rt = ids_t.index(d) + 1 if d in ids_t else None
        rb = ids_b.index(d) + 1 if d in ids_b else None
        rows.append({
            "doc_id": d, "judul": engine.docs.loc[d, "title"],
            "peringkat TF-IDF": rt, "peringkat BM25": rb,
            "perubahan": (rt - rb) if rt and rb else None,
            "TF term query": ", ".join(f"{t}:{engine.index.tf(t, d)}" for t in res_b["terms"]),
            "panjang (token)": engine.index.doc_len[d],
        })
    st.dataframe(
        pd.DataFrame(rows), hide_index=True,
        column_config={
            "perubahan": st.column_config.NumberColumn(
                help="Positif = naik peringkat di BM25 dibanding TF-IDF", format="%+d"),
        },
    )
    st.caption("Kosong pada kolom peringkat berarti dokumen tidak masuk Top-k metode tersebut.")

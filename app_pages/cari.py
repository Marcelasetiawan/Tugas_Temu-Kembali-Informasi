import streamlit as st

from src.app_utils import (EXAMPLE_QUERIES, METHOD_LABELS, get_engine, search_box, show_query_info,
                           show_results)
from src.ui import steps_row

engine = get_engine()

with st.container(key="card_sky_cari_1"):
    query = search_box("cari", "Query", EXAMPLE_QUERIES, placeholder="contoh: ritual pemakaman suku toraja",
                       help="Tekan Enter untuk mencari")
    with st.container(horizontal=True, vertical_alignment="bottom"):
        method = st.segmented_control("Metode ranking", list(METHOD_LABELS), default="BM25",
                                      required=True, key="cari_method")
        top_k = st.slider("Top-k", min_value=1, max_value=20, value=10, key="cari_topk")

if query.strip():
    res = engine.search(query, method=METHOD_LABELS[method], top_k=top_k)
    show_query_info(res)
    show_results(res)
else:
    steps_row([
        ("Ketik kata kunci", "Misalnya tari topeng, lalu tekan Enter. Atau klik salah satu contoh berwarna di atas."),
        ("Pilih metode", "BM25 disarankan. TF-IDF + Cosine bisa dipakai sebagai pembanding."),
        ("Atur Top-k", "Geser untuk menentukan jumlah hasil yang ditampilkan (1–20)."),
        ("Baca hasilnya", "Peringkat 1 paling cocok. Kata yang cocok ditebalkan di cuplikan."),
    ])

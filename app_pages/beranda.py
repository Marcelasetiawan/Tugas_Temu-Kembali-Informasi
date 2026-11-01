import altair as alt
import pandas as pd
import streamlit as st

from src.app_utils import documents_table, get_engine, get_evaluation
from src.ui import banner, bar_chart, bar_list, card_title, fmt_angka, kpi_cards, transparent

PALETTE = ["#2563EB", "#EA6A35", "#21A876", "#F2B01E", "#E5739D", "#5B3FC4"]

engine = get_engine()
idx = engine.index
docs = documents_table(engine)
_, ev = get_evaluation()

n_docs = idx.N
per_kat = docs["kategori"].value_counts()
f1 = ev.groupby("metode")["F1@10"].mean()
p5 = ev.groupby("metode")["P@5"].mean()

# ---------------- banner ----------------
banner("Selamat datang di Mesin Pencari Budaya Indonesia",
       f"Koleksi {n_docs} artikel tradisi dan kesenian dari Indonesia Kaya — "
       "ranking dengan TF-IDF + Cosine Similarity dan BM25")

# ---------------- kartu angka ----------------
kpi_cards([
    {"label": "Total dokumen", "value": n_docs, "sub": "artikel hasil crawling",
     "icon": "file", "color": "#4F3CC9", "pct": 100},
    {"label": "Kategori tradisi", "value": per_kat.get("tradisi", 0),
     "sub": f"{100 * per_kat.get('tradisi', 0) / n_docs:.1f}% dari total",
     "icon": "landmark", "color": "#EA6A35", "pct": 100 * per_kat.get("tradisi", 0) / n_docs},
    {"label": "Kategori kesenian", "value": per_kat.get("kesenian", 0),
     "sub": f"{100 * per_kat.get('kesenian', 0) / n_docs:.1f}% dari total",
     "icon": "palette", "color": "#2563EB", "pct": 100 * per_kat.get("kesenian", 0) / n_docs},
    {"label": "Jumlah term (vocabulary)", "value": fmt_angka(len(idx.vocabulary)),
     "sub": "term unik di inverted index", "icon": "hash", "color": "#21A876", "pct": 100},
    {"label": "Total token", "value": fmt_angka(sum(idx.doc_len.values())),
     "sub": "setelah prapemrosesan", "icon": "layers", "color": "#E5739D", "pct": 100},
    {"label": "Rata-rata panjang", "value": f"{idx.avgdl:.0f}",
     "sub": "token per dokumen (avgdl)", "icon": "ruler", "color": "#F2B01E",
     "pct": 100 * idx.avgdl / max(idx.doc_len.values())},
    {"label": "F1@10 TF-IDF + Cosine", "value": f"{f1['TF-IDF']:.3f}",
     "sub": f"P@5 = {p5['TF-IDF']:.3f}", "icon": "target", "color": "#0EA5E9", "pct": 100 * f1["TF-IDF"]},
    {"label": "F1@10 BM25", "value": f"{f1['BM25']:.3f}",
     "sub": f"P@5 = {p5['BM25']:.3f}", "icon": "award", "color": "#16A34A", "pct": 100 * f1["BM25"]},
])

# ---------------- donat kategori + 10 term teratas ----------------
left, right = st.columns([1.15, 1], gap="medium")

with left:
    with st.container(key="card_sky_kategori"):
        card_title("Sebaran kategori dokumen", "Jumlah artikel per kategori Pustaka Indonesia")
        donut_col, legend_col = st.columns([1, 1], vertical_alignment="center")
        kat_df = per_kat.rename_axis("kategori").reset_index(name="jumlah")
        kat_df["persen"] = (100 * kat_df["jumlah"] / n_docs).round(1)
        color = alt.Color("kategori:N", scale=alt.Scale(domain=list(kat_df["kategori"]),
                                                        range=["#2563EB", "#EA6A35"]), legend=None)
        ring = alt.Chart(kat_df).mark_arc(innerRadius=62, outerRadius=95).encode(
            theta="jumlah:Q", color=color, tooltip=["kategori", "jumlah", "persen"])
        center = alt.Chart(pd.DataFrame({"t": [str(n_docs)]})).mark_text(
            fontSize=26, fontWeight="bold", color="#16213E", dy=-6).encode(text="t:N")
        center2 = alt.Chart(pd.DataFrame({"t": ["dokumen"]})).mark_text(
            fontSize=12, color="#6B7590", dy=16).encode(text="t:N")
        with donut_col:
            st.altair_chart(transparent((ring + center + center2).properties(height=220)), width="stretch")
        with legend_col:
            for (_, r), c in zip(kat_df.iterrows(), ["#2563EB", "#EA6A35"]):
                st.html(f'<div class="tb-row" style="grid-template-columns:16px 1fr auto">'
                        f'<span style="width:12px;height:12px;border-radius:3px;background:{c}"></span>'
                        f'<span class="tb-row-label">{r["kategori"].capitalize()}</span>'
                        f'<span class="tb-row-val">{r["jumlah"]} · {r["persen"]}%</span></div>')

with right:
    with st.container(key="card_peach_terms"):
        card_title("10 term dengan document frequency tertinggi",
                   "Jumlah dokumen yang memuat term (setelah stemming)")
        top = sorted(((t, idx.df(t)) for t in idx.vocabulary), key=lambda x: -x[1])[:10]
        bar_list(top, PALETTE)

# ---------------- panjang dokumen + evaluasi ----------------
left, right = st.columns(2, gap="medium")

with left:
    with st.container(key="card_mint_panjang"):
        card_title("Sebaran panjang dokumen", "Jumlah dokumen per rentang jumlah token")
        bins = pd.cut(docs["jumlah_token"], bins=[0, 150, 300, 450, 600, 900, 1200, 2000],
                      labels=["0–150", "150–300", "300–450", "450–600", "600–900", "900–1200", "1200+"])
        dist = bins.value_counts(sort=False).rename_axis("token").reset_index(name="jumlah dokumen")
        bar_chart(dist, x="token", y="jumlah dokumen", single_color="#21A876")

with right:
    with st.container(key="card_lavender_evaluasi"):
        card_title("Rata-rata evaluasi", "18 query uji · TF-IDF + Cosine vs BM25")
        cols = ["P@5", "R@5", "F1@5", "P@10", "R@10", "F1@10"]
        long = (ev.groupby("metode")[cols].mean().reset_index()
                .melt(id_vars="metode", var_name="metrik", value_name="nilai"))
        bar_chart(long, x="metrik", y="nilai", color="metode")

# ---------------- pintasan ----------------
with st.container(key="card_butter_pintasan"):
    card_title("Mulai menggunakan", "Alur: koleksi → prapemrosesan → indexing → retrieval → ranking → Top-k")
    with st.container(horizontal=True):
        st.page_link("app_pages/panduan.py", label="Panduan pemakaian", icon=":material/menu_book:")
        st.page_link("app_pages/cari.py", label="Cari dokumen", icon=":material/search:")
        st.page_link("app_pages/bandingkan.py", label="Bandingkan metode", icon=":material/compare_arrows:")
        st.page_link("app_pages/evaluasi.py", label="Lihat evaluasi", icon=":material/analytics:")
        st.page_link("app_pages/index_explorer.py", label="Jelajahi inverted index", icon=":material/account_tree:")

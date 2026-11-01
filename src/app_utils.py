"""Fungsi bersama untuk antarmuka Streamlit (dipakai oleh app.py dan app_pages/)."""

import re

import pandas as pd
import streamlit as st

from src.evaluation import evaluate, load_queries
from src.search_engine import ROOT, SearchEngine

QUERIES_PATH = ROOT / "evaluation" / "queries.csv"
METHOD_LABELS = {"BM25": "bm25", "TF-IDF + Cosine": "tfidf"}
EXAMPLE_QUERIES = [
    "ritual pemakaman suku toraja",
    "alat musik bambu dari sunda",
    "kain tenun tradisional",
    "tari topeng",
    "angklung",
]


@st.cache_resource(show_spinner="Memuat dataset dan membangun inverted index ...")
def get_engine():
    """Mesin pencari dibangun sekali lalu dipakai bersama semua halaman."""
    return SearchEngine(verbose=False)


@st.cache_data(show_spinner="Menghitung evaluasi ...")
def get_evaluation():
    """Hasil evaluasi P/R/F1 seluruh query uji untuk kedua metode."""
    queries = load_queries(QUERIES_PATH)
    return queries, evaluate(get_engine(), queries, ks=(5, 10))


def search_box(prefix, label, examples, examples_label="Contoh query", **input_kwargs):
    """Kotak pencarian + tombol Kosongkan + contoh yang bisa diklik.

    Nilai disimpan di session_state[f"{prefix}_query"]; awalnya kosong, atau diisi
    dari URL jika ada parameter ?q=... (misalnya /cari?q=tari+topeng).
    Contoh memakai tombol biasa (bukan st.pills) agar tidak ada pilihan yang
    tertinggal di browser lalu mengisi ulang query saat kotak dikosongkan.
    """
    key = f"{prefix}_query"
    st.session_state.setdefault(key, st.query_params.get("q", ""))

    def set_query(text):
        st.session_state[key] = text

    with st.container(horizontal=True, vertical_alignment="bottom"):
        query = st.text_input(label, key=key, **input_kwargs)
        st.button("Kosongkan", icon=":material/close:", key=f"{prefix}_clear", on_click=set_query,
                  args=("",), disabled=not st.session_state[key], width="content")
    st.caption(examples_label)
    with st.container(horizontal=True, gap="small", key=f"{prefix}_examples"):
        for i, ex in enumerate(examples):
            st.button(ex, key=f"{prefix}_ex_{i}", on_click=set_query, args=(ex,), width="content")
    return query


def highlight(text, words):
    """Menebalkan kata yang cocok dengan term query."""
    for w in sorted(set(words), key=len, reverse=True):
        text = re.sub(rf"\b({re.escape(w)})\b", r"**\1**", text, flags=re.IGNORECASE)
    return text


def show_query_info(res):
    """Baris info: term hasil prapemrosesan dan jumlah kandidat."""
    with st.container(horizontal=True, vertical_alignment="center"):
        st.caption("Term query:", width="content")
        for t in res["terms"] or ["-"]:
            st.badge(t, color="gray")
        st.caption(f"· {res['n_candidates']} dokumen kandidat · {res['method']}", width="content")


def show_results(res, relevant=None):
    """Menampilkan hasil pencarian sebagai kartu. relevant: set doc_id relevan (opsional)."""
    if res["message"]:
        st.warning(res["message"], icon=":material/search_off:")
        return
    for r in res["results"]:
        with st.container(key=f"card_hasil_{res['method']}_{r['rank']}".replace(" ", "").replace("+", "")):
            with st.container(horizontal=True, vertical_alignment="center"):
                st.badge(f"#{r['rank']}", color="primary")
                st.markdown(f"**[{r['title']}]({r['url']})**")
                if relevant is not None and r["doc_id"] in relevant:
                    st.badge("relevan", icon=":material/check:", color="green")
            st.caption(f"Skor {r['score']:.4f} · {r['doc_id']} · {r['url']}")
            st.markdown(highlight(r["snippet"], r["matched"]))


def documents_table(engine):
    """Tabel ringkas seluruh dokumen."""
    df = engine.df
    return pd.DataFrame({
        "doc_id": df["doc_id"],
        "judul": df["title"],
        "kategori": df.get("kategori", ""),
        "jumlah_kata": df.get("jumlah_kata", df["content"].str.split().str.len()),
        "jumlah_token": df["jumlah_token"],
        "url": df["url"],
    })

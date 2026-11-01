import pandas as pd
import streamlit as st

from src.app_utils import get_engine, search_box
from src.ui import steps_row

engine = get_engine()
idx = engine.index

with st.container(key="card_sky_index_explorer_1"):
    word = search_box("idx", "Kata", ["toraja", "tarian", "pemakaman", "gamelan", "budaya"], "Contoh",
                      placeholder="contoh: angklung",
                      help="Kata diproses dulu (case folding, stemming, dll.) menjadi term")

if not word.strip():
    steps_row([
        ("Ketik satu kata", "Misalnya toraja, lalu tekan Enter. Atau klik contoh berwarna di atas."),
        ("DF", "Jumlah dokumen yang memuat kata tersebut."),
        ("IDF", "Makin jarang kata, makin tinggi nilainya, makin penting saat pencarian."),
        ("Postings list", "Daftar dokumen yang memuat kata itu beserta TF (berapa kali muncul)."),
    ])
    st.stop()

terms = engine.pre.preprocess(word)

if not terms:
    st.warning("Kata tersebut adalah stopword atau tidak mengandung huruf.", icon=":material/info:")
    st.stop()

term = terms[0]
if term not in idx.index:
    st.warning(f"Term **{term}** tidak ada di inverted index.", icon=":material/search_off:")
    st.stop()

st.markdown(f"Kata **{word}** → term **{term}**")
with st.container(horizontal=True):
    st.metric("Document frequency (DF)", idx.df(term), border=True)
    st.metric("IDF = log10(N/DF)", f"{engine.tfidf.idf[term]:.4f}", border=True)
    st.metric("IDF BM25", f"{engine.bm25.idf[term]:.4f}", border=True)
    st.metric("Total kemunculan", sum(idx.index[term].values()), border=True)

postings = pd.DataFrame([
    {"doc_id": d, "judul": engine.docs.loc[d, "title"], "TF": tf,
     "panjang (token)": idx.doc_len[d], "TF-IDF = TF x IDF": tf * engine.tfidf.idf[term]}
    for d, tf in idx.index[term].items()
]).sort_values("TF", ascending=False)

with st.container(key="card_lavender_index_explorer_2"):
    st.subheader("Postings list")
    st.code(f"{term} → {list(idx.index[term])[:30]}{' ...' if idx.df(term) > 30 else ''}", language=None)
    st.dataframe(
        postings, hide_index=True,
        column_config={
            "TF": st.column_config.ProgressColumn("TF", format="%d", min_value=0,
                                                  max_value=int(postings["TF"].max())),
            "TF-IDF = TF x IDF": st.column_config.NumberColumn(format="%.4f"),
        },
    )

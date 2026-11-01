import streamlit as st


with st.container(key="card_sky_tentang_1"):
    st.subheader("Alur sistem")
    st.markdown(
        "1. **Prapemrosesan** — case folding, normalisasi, tokenisasi, stopword removal, stemming Sastrawi "
        "(nama diri tidak di-stem).\n"
        "2. **Indexing** — inverted index: term → {doc_id: TF}.\n"
        "3. **Query processing** — query diproses dengan pipeline yang sama dengan dokumen.\n"
        "4. **Retrieval** — dokumen kandidat diambil dari postings list term query.\n"
        "5. **Scoring & ranking** — TF-IDF + cosine similarity atau BM25, diurutkan dari skor terbesar.\n"
        "6. **Top-k** — ditampilkan dengan judul, URL, skor, dan snippet."
    )

left, right = st.columns(2)
with left:
    with st.container(key="card_mint_tentang_2"):
        st.subheader("TF-IDF dan cosine similarity")
        st.latex(r"TF(t,d) = \text{jumlah kemunculan } t \text{ di } d")
        st.latex(r"IDF(t) = \log_{10}\frac{N}{df(t)}")
        st.latex(r"w_{t,d} = TF(t,d) \times IDF(t)")
        st.latex(r"\cos(q,d) = \frac{\vec{q}\cdot\vec{d}}{\lVert\vec{q}\rVert\,\lVert\vec{d}\rVert}")
with right:
    with st.container(key="card_peach_tentang_3"):
        st.subheader("BM25")
        st.latex(r"\text{score}(D,Q)=\sum_{t\in Q} IDF(t)\cdot\frac{f(t,D)\,(k_1+1)}"
                 r"{f(t,D)+k_1\left(1-b+b\frac{|D|}{avgdl}\right)}")
        st.latex(r"IDF(t)=\ln\left(1+\frac{N-df(t)+0.5}{df(t)+0.5}\right)")
        st.markdown("Parameter: **k1 = 1,2** (saturasi TF) dan **b = 0,75** (normalisasi panjang dokumen).")

with st.container(key="card_lavender_tentang_4"):
    st.subheader("Evaluasi")
    st.latex(r"P@k=\frac{|\text{relevan}\cap\text{Top-}k|}{k}\qquad "
             r"R@k=\frac{|\text{relevan}\cap\text{Top-}k|}{|\text{relevan}|}\qquad "
             r"F1@k=\frac{2\cdot P@k\cdot R@k}{P@k+R@k}")
    st.caption("Ground truth: 18 query, disusun manual dengan kriteria tertulis (judul + pooling Top-10).")

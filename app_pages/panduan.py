import pandas as pd
import streamlit as st

from src.app_utils import EXAMPLE_QUERIES, get_engine, search_box
from src.ui import card_title, steps_row

engine = get_engine()
idx = engine.index

# ---------------- apa ini ----------------
with st.container(key="card_sky_panduan_1"):
    card_title("Aplikasi ini apa?")
    st.markdown(
        f"Bayangkan **Google versi kecil** yang hanya berisi **{idx.N} artikel budaya Indonesia** "
        "(tradisi dan kesenian) dari situs Indonesia Kaya. Anda mengetik kata kunci, lalu sistem "
        "mencari artikel yang paling cocok dan mengurutkannya dari yang **paling relevan**."
    )

# ---------------- cara kerja ----------------
with st.container(key="card_lavender_panduan_2"):
    card_title("Cara kerjanya dalam 4 langkah")
    steps_row([
        ("Artikel dikumpulkan", f"{idx.N} artikel diambil dari Indonesia Kaya saat Tugas 1 (crawling)."),
        ("Teks dibersihkan", "Huruf dikecilkan, tanda baca dibuang, kata umum (yang, dan, di) dihapus, "
                             "kata dijadikan kata dasar: tarian → tari."),
        ("Dibuat indeks kata", "Seperti indeks di belakang buku: setiap kata dicatat muncul di "
                               "dokumen mana saja dan berapa kali."),
        ("Query dicocokkan & diberi skor", "Kata kunci Anda dibersihkan dengan cara yang sama, lalu tiap "
                                           "dokumen diberi skor (TF-IDF atau BM25) dan diurutkan."),
    ])

# ---------------- contoh nyata ----------------
with st.container(key="card_mint_panduan_3"):
    card_title("Lihat langsung prosesnya", "Pilih sebuah query, lalu ikuti apa yang terjadi di setiap langkah")
    st.session_state.setdefault("panduan_query", "Tarian-tarian tradisional dari Bali")
    query = search_box("panduan", "Query", ["Tarian-tarian tradisional dari Bali"] + EXAMPLE_QUERIES,
                       placeholder="ketik query sendiri, lalu tekan Enter")
    if not query.strip():
        st.info("Ketik sebuah query lalu tekan Enter, atau klik salah satu contoh.", icon=":material/keyboard:")
    else:
        res = engine.search(query, method="bm25", top_k=3)

        st.markdown("**Langkah 2 — teks query dibersihkan**")
        steps = engine.pre.steps(query)
        st.dataframe(pd.DataFrame({"tahap": list(steps),
                                   "hasil": [s if isinstance(s, str) else ", ".join(s) for s in steps.values()]}),
                     hide_index=True)

        st.markdown("**Langkah 3 — kata dicari di indeks**")
        st.dataframe(pd.DataFrame([{"kata (term)": t, "muncul di berapa dokumen": idx.df(t)}
                                   for t in dict.fromkeys(res["terms"])]), hide_index=True)
        st.caption(f"Dokumen yang memuat minimal satu kata tersebut: **{res['n_candidates']}** dokumen. "
                   "Hanya dokumen ini yang diberi skor.")

        st.markdown("**Langkah 4 — diberi skor dan diurutkan (3 teratas, BM25)**")
        if res["results"]:
            st.dataframe(pd.DataFrame([{"peringkat": r["rank"], "judul": r["title"], "skor": round(r["score"], 3)}
                                       for r in res["results"]]), hide_index=True)
        else:
            st.info(res["message"])
        st.caption("Skor bukan persen. Skor hanya dipakai untuk mengurutkan: makin besar, makin cocok.")

# ---------------- menu ----------------
with st.container(key="card_peach_panduan_4"):
    card_title("Menu mana untuk apa?")
    st.dataframe(pd.DataFrame([
        ("Dashboard", "Melihat ringkasan koleksi dan hasil evaluasi", "Cukup dibaca, tidak perlu mengisi apa pun"),
        ("Cari dokumen", "Mencari artikel (fitur utama)", "Ketik kata kunci → Enter, atau klik contoh"),
        ("Bandingkan metode", "Melihat beda hasil TF-IDF dan BM25", "Ketik satu query, hasil tampil kiri-kanan"),
        ("Boolean retrieval", "Pencarian cocok persis dengan AND / OR / NOT",
         "Contoh: wayang AND (kulit OR golek)"),
        ("Inverted index", "Melihat satu kata muncul di dokumen mana saja", "Ketik satu kata, misalnya toraja"),
        ("Evaluasi", "Melihat seberapa tepat hasil pencarian", "Pilih jenis query dan metrik"),
        ("Koleksi dokumen", "Melihat daftar semua artikel", "Saring berdasarkan kategori atau judul"),
        ("Tentang sistem", "Rumus lengkap (untuk laporan)", "Cukup dibaca"),
    ], columns=["menu", "gunanya", "cara pakai"]), hide_index=True)

# ---------------- istilah ----------------
left, right = st.columns(2, gap="medium")
with left:
    with st.container(key="card_butter_panduan_5"):
        card_title("Arti istilah pencarian")
        st.markdown(
            "- **Query** — kata kunci yang Anda ketik.\n"
            "- **Term** — kata yang sudah dibersihkan dan dijadikan kata dasar.\n"
            "- **TF** (term frequency) — berapa kali sebuah kata muncul di satu dokumen.\n"
            "- **DF** (document frequency) — berapa dokumen yang memuat kata itu.\n"
            "- **IDF** — makin jarang sebuah kata, makin tinggi nilainya, jadi makin "
            "menentukan. Kata *budaya* muncul di banyak artikel, jadi IDF-nya kecil.\n"
            "- **TF-IDF + Cosine** — metode yang mengukur kemiripan query dengan dokumen (skor 0–1).\n"
            "- **BM25** — metode skor yang juga memperhitungkan panjang dokumen, sehingga artikel "
            "panjang tidak otomatis menang.\n"
            "- **Top-k** — jumlah hasil teratas yang ditampilkan."
        )
with right:
    with st.container(key="card_rose_panduan_6"):
        card_title("Arti istilah evaluasi")
        st.markdown(
            "Untuk 18 query uji sudah ditentukan **jawaban benarnya** (dokumen yang relevan). "
            "Hasil sistem lalu dibandingkan dengan jawaban itu.\n\n"
            "- **P@5** (precision) — dari 5 hasil teratas, berapa bagian yang benar. "
            "Contoh: 4 benar dari 5 → 0,8.\n"
            "- **R@10** (recall) — dari semua dokumen yang benar, berapa bagian yang berhasil "
            "masuk 10 besar.\n"
            "- **F1** — gabungan precision dan recall dalam satu angka.\n\n"
            "Semua nilai berada di antara **0 dan 1**: makin mendekati 1, makin baik."
        )

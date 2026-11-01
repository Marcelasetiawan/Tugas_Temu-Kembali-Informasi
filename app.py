"""
Dashboard mesin pencari budaya Indonesia (Streamlit, multipage).

Menjalankan (dari folder tugas2_ir):
    streamlit run app.py
"""

import streamlit as st

from src.app_utils import get_engine
from src.ui import inject_css, page_header, sidebar_brand, sidebar_footer, sidebar_section

st.set_page_config(page_title="Mesin pencari budaya", page_icon=":material/search:", layout="wide")

# (judul menu, file, ikon, subjudul header, petunjuk "cara memakai halaman ini")
MENU = {
    "": [
        ("Dashboard", "app_pages/beranda.py", ":material/home:",
         "Gambaran umum koleksi dokumen dan kinerja mesin pencari",
         "Halaman ini **cukup dibaca**, tidak perlu mengisi apa pun.\n"
         "- **Kartu angka** di atas: jumlah artikel, kata unik, dan nilai evaluasi.\n"
         "- **Grafik donat**: perbandingan jumlah artikel tradisi dan kesenian.\n"
         "- **10 term teratas**: kata yang muncul di paling banyak artikel.\n"
         "- **Rata-rata evaluasi**: seberapa tepat hasil pencarian (0–1, makin tinggi makin baik).\n\n"
         "Baru pertama kali? Buka menu **Panduan pemakaian**."),
        ("Panduan pemakaian", "app_pages/panduan.py", ":material/menu_book:",
         "Cara kerja mesin pencari dan cara memakai setiap menu", None),
    ],
    "Pencarian": [
        ("Cari dokumen", "app_pages/cari.py", ":material/search:",
         "Cari artikel budaya dengan BM25 atau TF-IDF + cosine similarity",
         "1. Ketik kata kunci, misalnya **tari topeng**, lalu tekan **Enter**. Bisa juga klik salah satu contoh.\n"
         "2. Pilih **metode ranking**. BM25 biasanya sedikit lebih baik untuk artikel yang panjangnya beragam.\n"
         "3. Geser **Top-k** untuk mengatur jumlah hasil.\n\n"
         "Hasil nomor 1 adalah yang paling cocok. Kata yang cocok ditebalkan di cuplikan. "
         "**Skor bukan persen**, hanya untuk mengurutkan. Klik **Kosongkan** untuk mulai dari awal."),
        ("Bandingkan metode", "app_pages/bandingkan.py", ":material/compare_arrows:",
         "Query yang sama dijalankan dengan dua metode ranking",
         "Ketik satu query. Hasil **TF-IDF + Cosine** tampil di kiri dan **BM25** di kanan.\n"
         "- **Dokumen sama**: berapa dokumen yang muncul di kedua hasil.\n"
         "- **Tabel perubahan peringkat**: dokumen mana yang naik atau turun jika metode diganti."),
        ("Boolean retrieval", "app_pages/boolean.py", ":material/rule:",
         "Pencarian exact match dengan operator AND, OR, NOT",
         "Mencari dokumen yang **cocok persis** dengan aturan, tanpa skor dan tanpa urutan.\n"
         "- **AND**: kedua kata harus ada. **OR**: salah satu kata cukup. **NOT**: kata tidak boleh ada.\n"
         "- Tulis operator dengan **huruf besar**, kurung untuk mengelompokkan.\n\n"
         "Contoh: `wayang AND (kulit OR golek)` = artikel tentang wayang yang menyebut kulit atau golek."),
    ],
    "Analisis": [
        ("Inverted index", "app_pages/index_explorer.py", ":material/account_tree:",
         "Postings list, TF, DF, dan IDF setiap term",
         "Ketik **satu kata** untuk melihat kata itu muncul di dokumen mana saja, seperti indeks di "
         "belakang buku.\n"
         "- **DF**: jumlah dokumen yang memuat kata itu.\n"
         "- **IDF**: makin jarang kata, makin tinggi nilainya (makin penting saat pencarian).\n"
         "- **TF** di tabel: berapa kali kata muncul di dokumen tersebut."),
        ("Evaluasi", "app_pages/evaluasi.py", ":material/analytics:",
         "Precision, Recall, dan F1 pada 18 query uji",
         "Untuk 18 query uji sudah ditentukan dokumen yang benar (relevan). Halaman ini menunjukkan "
         "seberapa banyak hasil sistem yang benar.\n"
         "- **P@5**: dari 5 hasil teratas, berapa bagian yang benar.\n"
         "- **R@10**: dari semua dokumen benar, berapa bagian yang masuk 10 besar.\n"
         "- **F1**: gabungan keduanya. Nilai 0–1, makin tinggi makin baik.\n"
         "- Angka kecil hijau/merah di kartu = selisih dengan metode lainnya.\n\n"
         "Di bagian paling bawah, pilih satu query untuk melihat hasil mana yang benar (tanda hijau **relevan**)."),
        ("Koleksi dokumen", "app_pages/koleksi.py", ":material/library_books:",
         "Seluruh artikel hasil crawling Tugas 1",
         "Daftar semua artikel. Pilih **kategori** atau ketik sebagian **judul** untuk menyaring."),
    ],
    "Info": [
        ("Tentang sistem", "app_pages/tentang.py", ":material/info:",
         "Alur sistem dan rumus yang digunakan",
         "Rumus lengkap yang dipakai, cocok untuk laporan. Penjelasan sederhananya ada di menu "
         "**Panduan pemakaian**."),
    ],
}

pages, subtitles, helps = {}, {}, {}
for section, items in MENU.items():
    for title, path, icon, sub, help_text in items:
        pages[path] = st.Page(path, title=title, icon=icon, default=(path == "app_pages/beranda.py"))
        subtitles[path], helps[path] = sub, help_text

# Navigasi bawaan disembunyikan; menu disusun sendiri di sidebar agar mirip dashboard
page = st.navigation(list(pages.values()), position="hidden")

inject_css()
engine = get_engine()

with st.sidebar:
    sidebar_brand()
    for section, items in MENU.items():
        if section:
            sidebar_section(section)
        for title, path, icon, *_ in items:
            st.page_link(pages[path], label=title, icon=icon)
    sidebar_footer(engine.index.N, len(engine.index.vocabulary))

current = next(p for p, pg in pages.items() if pg.title == page.title)
page_header(page.title, subtitles[current])
if helps[current]:
    with st.expander("Cara memakai halaman ini", icon=":material/help:"):
        st.markdown(helps[current])
page.run()

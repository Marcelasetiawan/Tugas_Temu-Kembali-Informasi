# Tugas 2 — Mesin Pencari Sederhana Budaya Indonesia

Mesin pencari berbasis classical Information Retrieval untuk koleksi **516 artikel budaya Indonesia (tradisi dan kesenian)** dari Indonesia Kaya, hasil crawling Tugas 1.

Metode ranking: **TF-IDF + Vector Space Model (cosine similarity)** dan **BM25** (k1 = 1,2; b = 0,75), ditambah Boolean retrieval sebagai pelengkap. Semua metode diimplementasikan sendiri dengan Python.

## Alur sistem

```
Koleksi Dokumen → Prapemrosesan → Indexing → Query Processing → Retrieval → Scoring → Ranking → Top-k → Antarmuka
```

1. **Prapemrosesan** – case folding, normalisasi, tokenisasi, stopword removal, dan stemming Sastrawi (nama diri tidak di-stem).
2. **Indexing** – inverted index `term → {doc_id: TF}` (11.639 term dari 516 dokumen).
3. **Query processing** – query diproses dengan pipeline yang sama dengan dokumen.
4. **Retrieval** – dokumen kandidat diambil dari postings list term query.
5. **Scoring & ranking** – skor TF-IDF + cosine similarity atau BM25, diurutkan dari skor terbesar.
6. **Top-k** – ditampilkan dengan peringkat, judul, URL, skor, dan snippet.

## Ringkasan hasil evaluasi

Rata-rata 18 query uji (12 query umum + 6 query pendek & spesifik), dengan ground truth yang disusun manual:

| Metode | P@5 | R@5 | F1@5 | P@10 | R@10 | F1@10 |
|---|---|---|---|---|---|---|
| TF-IDF + Cosine | 0,800 | 0,585 | 0,619 | 0,633 | 0,794 | 0,653 |
| BM25 | 0,778 | 0,574 | 0,603 | 0,617 | 0,805 | 0,643 |

Kedua metode hampir setara pada koleksi ini. BM25 unggul ketika satu term langka diulang-ulang oleh dokumen yang
tidak relevan, sedangkan TF-IDF + cosine unggul ketika dokumen relevan tidak memuat semua term query. Analisis
lengkap ada di notebook dan laporan; nilai per query tersimpan di `evaluation/hasil_evaluasi.csv`.

## Struktur folder

```
tugas2_ir/                             # setelah clone: Tugas_Temu-Kembali-Informasi/
├── data/
│   ├── dataset_crawling_ir.csv        # dataset hasil Tugas 1 (516 dokumen)
│   └── dataset_preprocessed.csv       # dataset setelah prapemrosesan
├── index/
│   ├── inverted_index.json            # inverted index: term -> {doc_id: tf}
│   └── stem_cache.json                # cache hasil stemming Sastrawi
├── src/
│   ├── preprocessing.py               # case folding, normalisasi, tokenisasi, stopword, stemming
│   ├── indexing.py                    # inverted index, TF, DF
│   ├── boolean_retrieval.py           # AND / OR / NOT
│   ├── tfidf_retrieval.py             # TF-IDF, VSM, cosine similarity
│   ├── bm25.py                        # BM25
│   ├── search_engine.py               # mesin pencari + antarmuka baris perintah
│   ├── evaluation.py                  # Precision@k, Recall@k, F1@k
│   ├── app_utils.py                   # fungsi bersama untuk dashboard Streamlit
│   └── ui.py                          # komponen tampilan (header, banner, kartu, ikon)
├── evaluation/
│   ├── queries.csv                    # 18 query uji + ground truth + kriteria relevansi
│   ├── hasil_evaluasi.csv             # nilai P/R/F1 setiap query dan metode
│   └── hasil_eksperimen1.csv          # Top-10 dan skor setiap query (Eksperimen 1)
├── Tugas2_Mesin_Pencari.ipynb         # notebook: penjelasan, perhitungan, eksperimen, analisis
├── app.py                             # dashboard web (Streamlit) + menu navigasi sidebar
├── app_pages/                         # halaman dashboard (beranda, cari, bandingkan, evaluasi, ...)
├── .streamlit/config.toml             # tema warna dashboard
├── requirements.txt
└── README.md
```

## Instalasi

Membutuhkan **Python 3.9 atau lebih baru** (diuji pada Python 3.10 dan 3.11). Untuk cara clone, dibutuhkan juga
[Git](https://git-scm.com/downloads).

### Cara 1 – Clone dari GitHub

```bash
git clone https://github.com/Marcelasetiawan/Tugas_Temu-Kembali-Informasi.git
cd Tugas_Temu-Kembali-Informasi
python -m pip install -r requirements.txt
```

### Cara 2 – Dari file ZIP

1. Di halaman GitHub repository, klik **Code → Download ZIP** (atau gunakan file ZIP hasil pengumpulan tugas).
2. Ekstrak file ZIP, lalu buka terminal di folder hasil ekstrak.
3. Pasang library:
   ```bash
   python -m pip install -r requirements.txt
   ```

### (Opsional) Memakai virtual environment

Agar library project tidak bercampur dengan library Python lain di komputer:

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # macOS / Linux
python -m pip install -r requirements.txt
```

Jika di komputer terdapat lebih dari satu versi Python, selalu pakai `python -m pip ...` (bukan `pip ...` saja)
agar library terpasang di Python yang sama dengan yang menjalankan program.

## Cara menjalankan

Semua perintah dijalankan dari **folder project**, yaitu `Tugas_Temu-Kembali-Informasi` (hasil clone) atau
folder hasil ekstrak ZIP. Folder yang benar adalah folder yang berisi `app.py`, `README.md`, dan folder `src`.

Mesin pencari memiliki **dua antarmuka yang sama-sama bisa dipakai**. Keduanya memakai mesin pencari, data, dan
metode ranking yang sama; bedanya hanya pada tampilan.

| Antarmuka | Perintah | Tampil di | Cocok untuk |
|---|---|---|---|
| Baris perintah (CLI) | `python -m src.search_engine` | Terminal | Mencoba pencarian dengan cepat, hasil berupa tabel teks |
| Dashboard web | `streamlit run app.py` | Browser (`http://localhost:8501`) | Pencarian dengan tampilan grafis, perbandingan metode, inverted index, evaluasi |

Jika perintah `streamlit` tidak dikenali, jalankan dashboard dengan `python -m streamlit run app.py`.
Selain itu, notebook `Tugas2_Mesin_Pencari.ipynb` berisi penjelasan dan perhitungan setiap tahap.

### 1. Notebook (penjelasan lengkap setiap tahap)

```bash
jupyter notebook Tugas2_Mesin_Pencari.ipynb
```

Atau buka di VS Code, pilih kernel Python yang sudah terpasang paket di atas, lalu **Run All**.
Notebook menampilkan contoh prapemrosesan, inverted index, perhitungan TF-IDF/cosine/BM25, tiga eksperimen wajib, evaluasi, dan analisis.

### 2. Mesin pencari versi baris perintah (CLI)

```bash
python -m src.search_engine
```

Perintah harus memakai `-m src.search_engine` (bukan `python src/search_engine.py`) karena file ini
mengimpor modul lain di folder `src`.

Saat program siap, tampil daftar contoh query beserta penjelasannya. Di kolom **Masukkan query**:

| Ketik | Hasil |
|---|---|
| Nomor `1`–`6` | Langsung mencari query contoh tersebut |
| Kata kunci sendiri, misalnya `rumah adat` | Mencari sesuai yang diketik |
| `contoh` | Menampilkan daftar contoh lagi |
| `keluar` (atau Ctrl+C) | Menutup program |

Setelah itu pilih metode ranking (`1` = BM25, `2` = TF-IDF + Cosine; Enter = BM25) dan jumlah hasil Top-k
(Enter = 10). Hasil ditampilkan sebagai tabel ringkasan (nomor, Doc ID, judul, skor), lalu detail setiap
dokumen (judul, skor, URL, dan snippet). Jika tidak ada dokumen yang cocok, program menampilkan pesan.

```
 Top-3 dokumen (diurutkan dari skor tertinggi)
┌─────┬────────┬──────────────────────────────────────────┬──────────┐
│  No │ Doc ID │ Judul                                    │     Skor │
├─────┼────────┼──────────────────────────────────────────┼──────────┤
│   1 │ D323   │ Tari Topeng Tua, Refleksi Lelaki Bali... │   7.4966 │
│   2 │ D271   │ Tari Topeng, Permainan Watak Penuh Makna │   7.4594 │
│   3 │ D322   │ Topeng Bali, Beragam Karakter dalam...   │   7.3831 │
└─────┴────────┴──────────────────────────────────────────┴──────────┘
```

### 3. Mesin pencari versi web (dashboard Streamlit)

```bash
streamlit run app.py
```

Tunggu sampai muncul `Local URL: http://localhost:8501`. Browser biasanya terbuka otomatis; jika tidak, buka
alamat tersebut secara manual. Untuk menghentikan dashboard, tekan **Ctrl+C** di terminal. Menu di sidebar kiri:

| Menu | Isi |
|---|---|
| Dashboard | Banner sambutan, kartu angka berikon, grafik donat kategori, 10 term DF tertinggi, sebaran panjang dokumen, rata-rata evaluasi |
| Panduan pemakaian | Cara kerja sistem dalam 4 langkah, contoh proses query langkah demi langkah, kegunaan setiap menu, arti istilah (TF, DF, IDF, BM25, P@k, R@k, F1) |
| Cari dokumen | Input query, pilihan metode (BM25 / TF-IDF + cosine), Top-k, contoh query yang bisa diklik, hasil berupa kartu (peringkat, judul, URL, skor, snippet) |
| Bandingkan metode | Hasil TF-IDF dan BM25 berdampingan, jumlah dokumen yang sama, tabel perubahan peringkat |
| Boolean retrieval | Query AND / OR / NOT beserta langkah pemrosesannya |
| Inverted index | DF, IDF, dan postings list (dengan TF) sebuah term |
| Evaluasi | Kartu P/R/F1, grafik per query, tabel evaluasi, detail Top-10 dengan tanda dokumen relevan |
| Koleksi dokumen | Tabel seluruh dokumen dengan filter kategori dan judul |
| Tentang sistem | Alur sistem dan rumus |

Query bisa langsung diisi lewat alamat, misalnya `http://localhost:8501/cari?q=tari+topeng`.

Setiap halaman memiliki kotak **"Cara memakai halaman ini"** di bawah judul yang menjelaskan cara memakai dan membaca isinya.

### 4. Menjalankan di Google Colab

**Cara A – clone dari GitHub** (paling mudah). Jalankan di sel Colab:

```python
!git clone https://github.com/Marcelasetiawan/Tugas_Temu-Kembali-Informasi.git
%cd Tugas_Temu-Kembali-Informasi
!pip install -q -r requirements.txt
```

**Cara B – upload ZIP.** Upload file ZIP project ke panel **Files**, lalu jalankan:

```python
!unzip -q nama_file.zip -d project
%cd project
!pip install -q -r requirements.txt
```

Sesuaikan `nama_file.zip`, dan jika setelah diekstrak `app.py` berada di dalam subfolder, tambahkan `%cd`
ke subfolder tersebut.

Setelah itu, mesin pencari bisa dicoba langsung di sel Colab:

```python
from src.search_engine import SearchEngine, print_result

engine = SearchEngine()
print_result(engine.search("tari topeng", method="bm25", top_k=5))     # BM25
print_result(engine.search("tari topeng", method="tfidf", top_k=5))    # TF-IDF + cosine
```

**Menjalankan notebook lengkap di Colab:**

1. Buka **File → Open notebook → GitHub**, masukkan `Marcelasetiawan/Tugas_Temu-Kembali-Informasi`, lalu pilih
   `Tugas2_Mesin_Pencari.ipynb`.
2. Pilih **Runtime → Run all**. Sel persiapan Colab di awal notebook otomatis meng-clone repository dan memasang
   library, karena notebook membutuhkan modul di folder `src`.

Dashboard Streamlit paling mudah dijalankan di komputer lokal (Cara menjalankan nomor 3), karena Colab tidak
menyediakan alamat `localhost` yang bisa dibuka langsung di browser.

## Contoh query

| Query | Keterangan |
|---|---|
| `ritual pemakaman suku toraja` | Rambu Solo, makam tebing Lemo/Londa, Passiliran, Ma'nene |
| `alat musik bambu dari sunda` | Calung dan angklung |
| `kain tenun tradisional` | Tenun Ternate, Maluku, Baduy, Sambas, Gringsing |
| `tari topeng` | Tari Topeng Tua, Tari Topeng (permainan watak), Topeng Bali |
| `angklung` | Query pendek dan spesifik |
| `smartphone android` | Contoh query yang tidak menemukan dokumen |

Contoh Boolean retrieval (halaman **Boolean retrieval** di dashboard, notebook, atau `engine.boolean.search(...)`):
`toraja AND (ritual OR makam)`, `wayang AND (kulit OR golek)`, `senjata AND dayak AND NOT tari`.

## Jika terjadi error

| Pesan | Penyebab dan solusi |
|---|---|
| `No module named 'src'` | Perintah tidak dijalankan dari folder project (folder yang berisi `app.py` dan `src`), atau file dijalankan langsung (`python src/search_engine.py` / tombol ▶ VS Code). Masuk ke folder project lalu pakai `python -m src.search_engine`. |
| `'streamlit' is not recognized ...` | Folder Scripts Python tidak ada di PATH. Jalankan dashboard dengan `python -m streamlit run app.py`. |
| `'git' is not recognized ...` | Git belum terpasang. Pasang dari https://git-scm.com/downloads, atau gunakan Cara 2 (Download ZIP). |
| `No module named 'pandas'` / `'Sastrawi'` | Perintah `python` memanggil versi Python yang belum dipasangi paket. Jalankan `python -m pip install -r requirements.txt` dengan Python yang sama, atau tulis jalur lengkap Python yang sudah berisi paket. |
| `'src.search_engine' is not recognized ...` | Bagian depan perintah tertinggal. Ketik lengkap `python -m src.search_engine`. |
| `Port 8501 is already in use` | Dashboard masih berjalan di terminal lain. Hentikan dengan Ctrl+C di terminal tersebut. |

## Catatan

- **Prapemrosesan pertama kali** tanpa `index/stem_cache.json` membutuhkan ±10 menit karena stemming Sastrawi lambat (±35 ms per kata). Dengan cache, seluruh sistem siap dalam beberapa detik.
- Nama diri (nama daerah, suku) tidak di-stem karena Sastrawi salah memotongnya (*bali → bal*, *maluku → malu*). Beberapa kesalahan stemming lain dikoreksi di `STEM_OVERRIDES` (*menikah → nikah*).
- Rumus TF-IDF dan BM25 mengikuti materi kuliah: TF = frekuensi mentah, IDF = log10(N/df), IDF BM25 = ln(1 + (N − df + 0,5)/(df + 0,5)).
